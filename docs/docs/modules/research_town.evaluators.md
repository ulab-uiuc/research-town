# research_town.evaluators package

## Submodules

## research_town.evaluators.evaluator_base module

### *class* research_town.evaluators.evaluator_base.BaseEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config))

Bases: `object`

#### evaluate_idea_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea)) → [IdeaEvalOutput](#research_town.evaluators.evaluator_output.IdeaEvalOutput)

#### evaluate_insight_quality(insight: [Insight](research_town.dbs.md#research_town.dbs.data.Insight)) → [InsightEvalOutput](#research_town.evaluators.evaluator_output.InsightEvalOutput)

#### evaluate_metareview_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), reviews: List[[Review](research_town.dbs.md#research_town.dbs.data.Review)], rebuttals: List[[Rebuttal](research_town.dbs.md#research_town.dbs.data.Rebuttal)], metareview: [MetaReview](research_town.dbs.md#research_town.dbs.data.MetaReview)) → [MetaReviewEvalOutput](#research_town.evaluators.evaluator_output.MetaReviewEvalOutput)

#### evaluate_paper_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal)) → [ProposalEvalOutput](#research_town.evaluators.evaluator_output.ProposalEvalOutput)

#### evaluate_rebuttal_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), review: [Review](research_town.dbs.md#research_town.dbs.data.Review), rebuttal: [Rebuttal](research_town.dbs.md#research_town.dbs.data.Rebuttal)) → [RebuttalEvalOutput](#research_town.evaluators.evaluator_output.RebuttalEvalOutput)

#### evaluate_review_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), review: [Review](research_town.dbs.md#research_town.dbs.data.Review)) → [ReviewEvalOutput](#research_town.evaluators.evaluator_output.ReviewEvalOutput)

#### pipeline_eval(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), reviews: List[[Review](research_town.dbs.md#research_town.dbs.data.Review)], rebuttals: List[[Rebuttal](research_town.dbs.md#research_town.dbs.data.Rebuttal)], metareview: [MetaReview](research_town.dbs.md#research_town.dbs.data.MetaReview)) → Tuple[List[[InsightEvalOutput](#research_town.evaluators.evaluator_output.InsightEvalOutput)], [IdeaEvalOutput](#research_town.evaluators.evaluator_output.IdeaEvalOutput), [ProposalEvalOutput](#research_town.evaluators.evaluator_output.ProposalEvalOutput), List[[ReviewEvalOutput](#research_town.evaluators.evaluator_output.ReviewEvalOutput)], List[[RebuttalEvalOutput](#research_town.evaluators.evaluator_output.RebuttalEvalOutput)], [MetaReviewEvalOutput](#research_town.evaluators.evaluator_output.MetaReviewEvalOutput)]

## research_town.evaluators.evaluator_output module

### *class* research_town.evaluators.evaluator_output.BaseEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: `BaseModel`

#### dimension_scores *: list[int]*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### overall_score *: int*

#### pk *: str*

#### *classmethod* validate_dimension_scores(v: list[int]) → list[int]

#### *classmethod* validate_overall_score(v: int) → int

### *class* research_town.evaluators.evaluator_output.IdeaEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.evaluators.evaluator_output.InsightEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.evaluators.evaluator_output.MetaReviewEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.evaluators.evaluator_output.ProposalEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.evaluators.evaluator_output.RebuttalEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.evaluators.evaluator_output.ReviewEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

## research_town.evaluators.evaluator_output_format module

### *exception* research_town.evaluators.evaluator_output_format.OutputFormatError(message: str = 'Output format error')

Bases: `Exception`

## research_town.evaluators.evaluator_quality module

### *class* research_town.evaluators.evaluator_quality.BaseQualityEvaluator(model_name: str, output_model: type[[BaseEvalOutput](#research_town.evaluators.evaluator_output.BaseEvalOutput)], config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: `object`

#### eval(\*args: Any, \*\*kwargs: Any) → [BaseEvalOutput](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### parse(raw_output: str, output_model: type[T]) → T

### *class* research_town.evaluators.evaluator_quality.IdeaQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [IdeaEvalOutput](#research_town.evaluators.evaluator_output.IdeaEvalOutput)

### *class* research_town.evaluators.evaluator_quality.InsightQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [InsightEvalOutput](#research_town.evaluators.evaluator_output.InsightEvalOutput)

### *class* research_town.evaluators.evaluator_quality.MetaReviewQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [MetaReviewEvalOutput](#research_town.evaluators.evaluator_output.MetaReviewEvalOutput)

### *class* research_town.evaluators.evaluator_quality.ProposalQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [ProposalEvalOutput](#research_town.evaluators.evaluator_output.ProposalEvalOutput)

### *class* research_town.evaluators.evaluator_quality.RebuttalQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [RebuttalEvalOutput](#research_town.evaluators.evaluator_output.RebuttalEvalOutput)

### *class* research_town.evaluators.evaluator_quality.ReviewQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [ReviewEvalOutput](#research_town.evaluators.evaluator_output.ReviewEvalOutput)

## Module contents

### *class* research_town.evaluators.BaseEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config))

Bases: `object`

#### evaluate_idea_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea)) → [IdeaEvalOutput](#research_town.evaluators.evaluator_output.IdeaEvalOutput)

#### evaluate_insight_quality(insight: [Insight](research_town.dbs.md#research_town.dbs.data.Insight)) → [InsightEvalOutput](#research_town.evaluators.evaluator_output.InsightEvalOutput)

#### evaluate_metareview_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), reviews: List[[Review](research_town.dbs.md#research_town.dbs.data.Review)], rebuttals: List[[Rebuttal](research_town.dbs.md#research_town.dbs.data.Rebuttal)], metareview: [MetaReview](research_town.dbs.md#research_town.dbs.data.MetaReview)) → [MetaReviewEvalOutput](#research_town.evaluators.evaluator_output.MetaReviewEvalOutput)

#### evaluate_paper_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal)) → [ProposalEvalOutput](#research_town.evaluators.evaluator_output.ProposalEvalOutput)

#### evaluate_rebuttal_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), review: [Review](research_town.dbs.md#research_town.dbs.data.Review), rebuttal: [Rebuttal](research_town.dbs.md#research_town.dbs.data.Rebuttal)) → [RebuttalEvalOutput](#research_town.evaluators.evaluator_output.RebuttalEvalOutput)

#### evaluate_review_quality(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), review: [Review](research_town.dbs.md#research_town.dbs.data.Review)) → [ReviewEvalOutput](#research_town.evaluators.evaluator_output.ReviewEvalOutput)

#### pipeline_eval(insights: List[[Insight](research_town.dbs.md#research_town.dbs.data.Insight)], idea: [Idea](research_town.dbs.md#research_town.dbs.data.Idea), paper: [Proposal](research_town.dbs.md#research_town.dbs.data.Proposal), reviews: List[[Review](research_town.dbs.md#research_town.dbs.data.Review)], rebuttals: List[[Rebuttal](research_town.dbs.md#research_town.dbs.data.Rebuttal)], metareview: [MetaReview](research_town.dbs.md#research_town.dbs.data.MetaReview)) → Tuple[List[[InsightEvalOutput](#research_town.evaluators.evaluator_output.InsightEvalOutput)], [IdeaEvalOutput](#research_town.evaluators.evaluator_output.IdeaEvalOutput), [ProposalEvalOutput](#research_town.evaluators.evaluator_output.ProposalEvalOutput), List[[ReviewEvalOutput](#research_town.evaluators.evaluator_output.ReviewEvalOutput)], List[[RebuttalEvalOutput](#research_town.evaluators.evaluator_output.RebuttalEvalOutput)], [MetaReviewEvalOutput](#research_town.evaluators.evaluator_output.MetaReviewEvalOutput)]

### *class* research_town.evaluators.IdeaEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### dimension_scores *: List[int]*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### overall_score *: int*

#### pk *: str*

### *class* research_town.evaluators.IdeaQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [IdeaEvalOutput](#research_town.evaluators.evaluator_output.IdeaEvalOutput)

### *class* research_town.evaluators.InsightEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### dimension_scores *: List[int]*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### overall_score *: int*

#### pk *: str*

### *class* research_town.evaluators.InsightQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [InsightEvalOutput](#research_town.evaluators.evaluator_output.InsightEvalOutput)

### *class* research_town.evaluators.MetaReviewEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### dimension_scores *: List[int]*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### overall_score *: int*

#### pk *: str*

### *class* research_town.evaluators.MetaReviewQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [MetaReviewEvalOutput](#research_town.evaluators.evaluator_output.MetaReviewEvalOutput)

### *exception* research_town.evaluators.OutputFormatError(message: str = 'Output format error')

Bases: `Exception`

### *class* research_town.evaluators.ProposalEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### dimension_scores *: List[int]*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### overall_score *: int*

#### pk *: str*

### *class* research_town.evaluators.ProposalQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [ProposalEvalOutput](#research_town.evaluators.evaluator_output.ProposalEvalOutput)

### *class* research_town.evaluators.RebuttalEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### dimension_scores *: List[int]*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### overall_score *: int*

#### pk *: str*

### *class* research_town.evaluators.RebuttalQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [RebuttalEvalOutput](#research_town.evaluators.evaluator_output.RebuttalEvalOutput)

### *class* research_town.evaluators.ReviewEvalOutput(\*, overall_score: int = -1, pk: str = '0', dimension_scores: list[int] = [], \*\*extra_data: Any)

Bases: [`BaseEvalOutput`](#research_town.evaluators.evaluator_output.BaseEvalOutput)

#### dimension_scores *: List[int]*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'dimension_scores': FieldInfo(annotation=list[int], required=False, default=[]), 'overall_score': FieldInfo(annotation=int, required=False, default=-1), 'pk': FieldInfo(annotation=str, required=False, default='0')  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### overall_score *: int*

#### pk *: str*

### *class* research_town.evaluators.ReviewQualityEvaluator(model_name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config) | None = None, \*args: Any, \*\*kwargs: Any)

Bases: [`BaseQualityEvaluator`](#research_town.evaluators.evaluator_quality.BaseQualityEvaluator)

#### eval(\*args: Any, \*\*kwargs: Any) → [ReviewEvalOutput](#research_town.evaluators.evaluator_output.ReviewEvalOutput)
