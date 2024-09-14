import os
import subprocess
import sys
from typing import Any, Dict, List, Literal, Optional, Union

from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model

from ..configs import Config
from ..dbs import Experiment, LogDB, PaperDB, ProgressDB, Proposal

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class ExperimentEnv:
    def __init__(
        self,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        config: Config,
        folder: str = 'experiments',
        max_loops: int = 5,
    ) -> None:
        self.log_db = log_db
        self.progress_db = progress_db
        self.paper_db = paper_db
        self.folder = folder  # Initialize the folder path
        self.max_loops = max_loops  # Initialize max_loops
        self.model_name = (
            config.param.experiment_model_name
        )  # best: 'claude-3-opus-20240229'

        self.model = Model(self.model_name)
        self.result = ''  # exec result
        self.prompt_template = """
        # Experiment Instructions

        ## Research Proposal
        {proposal}

        ## Requirements
        ...

        ## Task
        - Modify the files: {files}
        - Write the experiment script based on the proposal.
        - Ensure the script is executable.

        ## Completion
        When the experiment is successful, write `END_OF_EXPERIMENTS` in new line in chat mode, not in code. Do not change the script after this.

        ## Notes
        - Add comments to explain any changes.
        - Ensure the script runs without errors and produces valid results.

        Modify the files, the system will run the experiment, tell you result({result}), and you should then make adjustments as needed.
        """

    def _run_subprocess(self, command: List[str], cwd: Optional[str] = None) -> str:
        process = subprocess.Popen(
            command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        result = ''
        assert process
        assert process.stdout
        assert process.stderr
        for stdout_line in iter(process.stdout.readline, ''):
            print(stdout_line, end='')
            result += stdout_line + '\n'
        for stderr_line in iter(process.stderr.readline, ''):
            print(stderr_line, end='', file=sys.stderr)
            result += stderr_line + '\n'
        process.stdout.close()
        process.stderr.close()
        process.wait()
        return result

    def _read_from_text_file(self, path: str) -> str:
        with open(path, 'r') as f:
            return f.read()

    def run(self, time_step: int, paper_pk: str) -> None:
        conditions = {'pk': paper_pk}
        proposal = self.progress_db.get(Proposal, **conditions)[0].abstract
        # Define folder and file paths based on pk
        folder = os.path.join(self.folder, paper_pk)
        experiment_script = os.path.join(folder, 'experiment.py')
        # stdout_file = os.path.join(folder, 'experiment_stdout.txt')
        # stderr_file = os.path.join(folder, 'experiment_stderr.txt')
        aiderout_file = os.path.join(folder, 'aider_stdout.txt')

        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f'Created folder: {folder}')

        open(aiderout_file, 'w').close()

        # Update InputOutput instance with specific paths
        io = InputOutput(yes=True, chat_history_file=aiderout_file)
        coder = Coder.create(
            main_model=self.model,
            fnames=[experiment_script],
            stream=False,
            use_git=False,
            io=io,
        )

        prompt = self.prompt_template.format(
            proposal=proposal,
            files='experiment.py',
            result='This is the initial run, so no experiment results. ',
            next_url_prompt='',
        )

        # Run the coding agent with the current prompt
        coder.run(prompt)

        # Append results to the prompt
        self.result = self._run_subprocess([sys.executable, experiment_script])

        loop_counter = 1

        experiment_done = False

        while not experiment_done and loop_counter <= self.max_loops:
            next_url_prompt = ''
            if (
                'datasets.exceptions.DatasetNotFoundError: Dataset ' in self.result
            ) or ("Error loading dataset: Dataset '" in self.result):
                if 'datasets.exceptions.DatasetNotFoundError: Dataset ' in self.result:
                    wrong_dataset_name = self.result.split(
                        "datasets.exceptions.DatasetNotFoundError: Dataset '"
                    )[1]
                else:
                    wrong_dataset_name = self.result.split(
                        "Error loading dataset: Dataset '"
                    )[1]
                wrong_dataset_name = wrong_dataset_name[: wrong_dataset_name.find("'")]
                next_url_prompt = f"You attempted to load a dataset, but you failed. It is possible that you did not provide the correct name. Here is a page where you can find out the real name to use: https://huggingface.co/datasets?sort=trending&search={wrong_dataset_name}. The correct name is something like 'user_name/dataset_name'."

            prompt = self.prompt_template.format(
                proposal=proposal,
                files='experiment.py',
                result=self.result[-1024:],
                next_url_prompt=next_url_prompt,
            )

            # Run the coding agent with the updated prompt
            coder.run(prompt)

            # Read the AI's response
            response = self._read_from_text_file(aiderout_file)

            # Check if the AI indicates the end of the experiment
            response_lines = response.split('\n')
            for line in response_lines:
                if '####' in line:
                    continue
                if line == 'END_OF_EXPERIMENTS':
                    experiment_done = True
                    break

            if experiment_done:
                print('SUCCESS')
                loop_counter += 1
                break

            # Append results to the prompt
            self.result = self._run_subprocess([sys.executable, experiment_script])
            loop_counter += 1

        print('Final results:')
        print(self.result)
        self.experiment = Experiment(
            paper_pk=paper_pk,
            code=self._read_from_text_file(experiment_script),
            exec_result=self.result,
        )
        self.progress_db.add(self.experiment)
        # self.log_db.add(
        #    ExperimentLog(
        #        time_step=time_step, paper_pk=paper_pk, experiment_pk=self.experiment.pk
        #    )
        # )

        # return self.result

    def on_exit(self, *args: Any, **kwargs: Any) -> bool:
        # No specific actions needed on exiting the environment
        return True
