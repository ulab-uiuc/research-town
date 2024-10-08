# research_town.utils package

## Submodules

## research_town.utils.profile_collector module

### research_town.utils.profile_collector.coauthor_filter(co_authors: dict[str, int], limit: int = 5) → list[str]

### research_town.utils.profile_collector.coauthor_frequency(author: str, author_list: list[str], co_authors: dict[str, int]) → dict[str, int]

### research_town.utils.profile_collector.collect_publications_and_coauthors(author: str, paper_max_num: int = 10) → tuple[list[dict[str, Any]], list[str]]

## research_town.utils.agent_prompter module

### research_town.utils.agent_prompter.brainstorm_idea_prompting(bio: str, insights: list[dict[str, str]], model_name: str, prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → list[str]

### research_town.utils.agent_prompter.summarize_idea_prompting(ideas: list[dict[str, str]], model_name: str, prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → list[str]

### research_town.utils.agent_prompter.review_literature_prompting(profile: dict[str, str], papers: list[dict[str, str]], domains: list[str], contexts: list[str], model_name: str, prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → list[str]

### research_town.utils.profile_collector.write_bio_prompting(publication_info: str, prompt_template: dict[str, str | list[str]], model_name: str = 'gpt-4o-mini', return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → list[str]

Write bio based on personal research history

### research_town.utils.agent_prompter.write_metareview_prompting(proposal: dict[str, str], reviews: list[dict[str, int | str]], rebuttals: list[dict[str, str]], model_name: str, summary_prompt_template: dict[str, str | list[str]], strength_prompt_template: dict[str, str | list[str]], weakness_prompt_template: dict[str, str | list[str]], ethical_prompt_template: dict[str, str | list[str]], decision_prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → tuple[str, str, str, str, bool]

### research_town.utils.agent_prompter.write_proposal_prompting(idea: dict[str, str], papers: list[dict[str, str]], model_name: str, prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → tuple[str, dict[str, str]]

### research_town.utils.agent_prompter.write_rebuttal_prompting(proposal: dict[str, str], review: dict[str, int | str], model_name: str, prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → list[str]

### research_town.utils.agent_prompter.write_review_prompting(proposal: dict[str, str], model_name: str, summary_prompt_template: dict[str, str | list[str]], strength_prompt_template: dict[str, str | list[str]], weakness_prompt_template: dict[str, str | list[str]], ethical_prompt_template: dict[str, str | list[str]], score_prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → tuple[str, str, str, str, int]

## research_town.utils.error_handler module

### research_town.utils.error_handler.api_calling_error_exponential_backoff(retries: int = 5, base_wait_time: int = 1) → Callable[[T], T]

Decorator for applying exponential backoff to a function.
:param retries: Maximum number of retries.
:param base_wait_time: Base wait time in seconds for the exponential backoff.
:return: The wrapped function with exponential backoff applied.

### research_town.utils.error_handler.parsing_error_exponential_backoff(retries: int = 5, base_wait_time: int = 1) → Callable[[TBaseModel], TBaseModel]

Decorator for retrying a function that returns a BaseModel with exponential backoff.
:param retries: Maximum number of retries.
:param base_wait_time: Base wait time in seconds for the exponential backoff.
:return: The wrapped function with retry logic applied.

## research_town.utils.eval_prompter module

### research_town.utils.eval_prompter.research_idea_quality_eval_prompting(model_name: str, insights: list[dict[str, str]], idea: dict[str, str], prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → str

### research_town.utils.eval_prompter.research_insight_quality_eval_prompting(model_name: str, insight: dict[str, str], prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → str

### research_town.utils.eval_prompter.research_metareview_quality_eval_prompting(model_name: str, insights: list[dict[str, str]], idea: dict[str, str], paper: dict[str, str], reviews: list[dict[str, int | str]], rebuttals: list[dict[str, str]], metareview: dict[str, str], prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → str

### research_town.utils.eval_prompter.research_proposal_quality_eval_prompting(model_name: str, insights: list[dict[str, str]], idea: dict[str, str], paper: dict[str, str], prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → str

### research_town.utils.eval_prompter.research_rebuttal_quality_eval_prompting(model_name: str, insights: list[dict[str, str]], idea: dict[str, str], paper: dict[str, str], review: dict[str, int | str], rebuttal: dict[str, str], prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → str

### research_town.utils.eval_prompter.research_review_quality_eval_prompting(model_name: str, insights: list[dict[str, str]], idea: dict[str, str], paper: dict[str, str], review: dict[str, int | str], prompt_template: dict[str, str | list[str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None) → str

## research_town.utils.logger module

### *class* research_town.utils.logger.ColoredFormatter(fmt=None, datefmt=None, style='%', validate=True, \*, defaults=None)

Bases: `Formatter`

#### format(record: LogRecord) → Any

Format the specified record as text.

The record’s attribute dictionary is used as the operand to a
string formatting operation which yields the returned string.
Before formatting the dictionary, a couple of preparatory steps
are carried out. The message attribute of the record is computed
using LogRecord.getMessage(). If the formatting string uses the
time (as determined by a call to usesTime(), formatTime() is
called to format the event time. If there is exception information,
it is formatted using formatException() and appended to the message.

### research_town.utils.logger.get_console_handler() → Any

Returns a console handler for logging.

## research_town.utils.model_prompting module

### research_town.utils.model_prompting.model_prompting(llm_model: str, messages: list[dict[str, str]], return_num: int | None = 1, max_token_num: int | None = 512, temperature: float | None = 0.0, top_p: float | None = None, stream: bool | None = None, mode: str | None = None) → list[str]

Select model via router in LiteLLM.

## research_town.utils.paper_collector module

### research_town.utils.paper_collector.get_recent_papers(query: str, max_results: int = 2) → tuple[dict[str, dict[str, list[str]]], str]

### research_town.utils.paper_collector.get_paper_introduction(url: str) → str | None

### research_town.utils.paper_collector.get_paper_content_from_html(url: str) → tuple[dict[str, str] | None, dict[str, str] | None, dict[str, str] | None, dict[str, str] | None]

## research_town.utils.prompt_constructor module

### research_town.utils.prompt_constructor.openai_format_prompt_construct(template: Dict[str, str | List[str]], input_data: Dict[str, Any]) → List[Dict[str, str]]

## research_town.utils.retriever module

### research_town.utils.retriever.get_embed(instructions: ~typing.List[str], retriever_tokenizer: ~transformers.models.bert.tokenization_bert.BertTokenizer = BertTokenizer(name_or_path='facebook/contriever', vocab_size=30522, model_max_length=512, is_fast=False, padding_side='right', truncation_side='right', special_tokens=  'unk_token': '[UNK]', 'sep_token': '[SEP]', 'pad_token': '[PAD]', 'cls_token': '[CLS]', 'mask_token': '[MASK]'  , clean_up_tokenization_spaces=True),  added_tokens_decoder=   	0: AddedToken("[PAD]", rstrip=False, lstrip=False, single_word=False, normalized=False, special=True), 	100: AddedToken("[UNK]", rstrip=False, lstrip=False, single_word=False, normalized=False, special=True), 	101: AddedToken("[CLS]", rstrip=False, lstrip=False, single_word=False, normalized=False, special=True), 	102: AddedToken("[SEP]", rstrip=False, lstrip=False, single_word=False, normalized=False, special=True), 	103: AddedToken("[MASK]", rstrip=False, lstrip=False, single_word=False, normalized=False, special=True),   , retriever_model: ~transformers.models.bert.modeling_bert.BertModel = BertModel(   (embeddings): BertEmbeddings(     (word_embeddings): Embedding(30522, 768, padding_idx=0)     (position_embeddings): Embedding(512, 768)     (token_type_embeddings): Embedding(2, 768)     (LayerNorm): LayerNorm((768,), eps=1e-12, elementwise_affine=True)     (dropout): Dropout(p=0.1, inplace=False)   )   (encoder): BertEncoder(     (layer): ModuleList(       (0-11): 12 x BertLayer(         (attention): BertAttention(           (self): BertSdpaSelfAttention(             (query): Linear(in_features=768, out_features=768, bias=True)             (key): Linear(in_features=768, out_features=768, bias=True)             (value): Linear(in_features=768, out_features=768, bias=True)             (dropout): Dropout(p=0.1, inplace=False)           )           (output): BertSelfOutput(             (dense): Linear(in_features=768, out_features=768, bias=True)             (LayerNorm): LayerNorm((768,), eps=1e-12, elementwise_affine=True)             (dropout): Dropout(p=0.1, inplace=False)           )         )         (intermediate): BertIntermediate(           (dense): Linear(in_features=768, out_features=3072, bias=True)           (intermediate_act_fn): GELUActivation()         )         (output): BertOutput(           (dense): Linear(in_features=3072, out_features=768, bias=True)           (LayerNorm): LayerNorm((768,), eps=1e-12, elementwise_affine=True)           (dropout): Dropout(p=0.1, inplace=False)         )       )     )   )   (pooler): BertPooler(     (dense): Linear(in_features=768, out_features=768, bias=True)     (activation): Tanh()   ) )) → List[Tensor]

### research_town.utils.retriever.rank_topk(query_embed: List[Tensor], corpus_embed: List[Tensor], num: int) → List[List[int]]

## research_town.utils.role_verifier module

### research_town.utils.role_verifier.chair_required(method: F) → F

### research_town.utils.role_verifier.leader_required(method: F) → F

### research_town.utils.role_verifier.member_required(method: F) → F

### research_town.utils.role_verifier.reviewer_required(method: F) → F

## research_town.utils.serializer module

### *class* research_town.utils.serializer.Serializer

Bases: `object`

#### *classmethod* deserialize(data: dict[str, Any] | list[Any] | tuple[Any, ...] | set[Any] | str | int | bool) → Any

#### *classmethod* serialize(obj: Any) → Any

## research_town.utils.string_mapper module

### research_town.utils.string_mapper.map_idea_list_to_str(ideas: list[dict[str, str]]) → str

### research_town.utils.string_mapper.map_idea_to_str(idea: dict[str, str]) → str

### research_town.utils.string_mapper.map_insight_list_to_str(insights: list[dict[str, str]]) → str

### research_town.utils.string_mapper.map_insight_to_str(insight: dict[str, str]) → str

### research_town.utils.string_mapper.map_metareview_list_to_str(metareviews: list[dict[str, str]]) → str

### research_town.utils.string_mapper.map_metareview_to_str(metareview: dict[str, str]) → str

### research_town.utils.string_mapper.map_paper_list_to_str(papers: list[dict[str, str]]) → str

### research_town.utils.string_mapper.map_paper_to_str(paper: dict[str, str]) → str

### research_town.utils.string_mapper.map_proposal_list_to_str(papers: list[dict[str, str]]) → str

### research_town.utils.string_mapper.map_proposal_to_str(paper: dict[str, str]) → str

### research_town.utils.string_mapper.map_rebuttal_list_to_str(rebuttals: list[dict[str, str]]) → str

### research_town.utils.string_mapper.map_rebuttal_to_str(paper: dict[str, str]) → str

### research_town.utils.string_mapper.map_review_list_to_str(reviews: list[dict[str, int | str]]) → str

### research_town.utils.string_mapper.map_review_to_str(review: dict[str, int | str]) → str

## Module contents
