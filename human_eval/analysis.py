import pandas as pd

if __name__ == "__main__":
    human_real = pd.read_csv("./human_eval/data/human_real.csv")
    human_simulated = pd.read_csv("./human_eval/data/human_simulated.csv")
    llm_simulated = pd.read_csv("./human_eval/data/llm_simulated.csv")
    human_real_mean = human_real.groupby('Domain').mean().reset_index()
    human_simulated_mean = human_simulated.groupby(
        'Domain').mean().reset_index()
    llm_simulated_mean = llm_simulated.groupby(
        'Domain').mean().reset_index()
    print("Spearman's correlation coefficient")
    print(llm_simulated_mean.corrwith(
        human_simulated_mean, axis=0, method='spearman'))
