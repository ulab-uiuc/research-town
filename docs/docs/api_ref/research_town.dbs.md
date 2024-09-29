# research_town.dbs package

## Submodules

## research_town.data module

### *class* research_town.data.Data(\*, pk: str = None, project_name: str | None = None)

Bases: `BaseModel`

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory=[lambda]), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

### *class* research_town.data.Idea(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.data.IdeaBrainstormLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, idea_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### idea_pk *: str*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'idea_pk': FieldInfo(annotation=str, required=True), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.data.Insight(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.data.LiteratureReviewLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, insight_pk: str | None = None)

Bases: [`Log`](#research_town.data.Log)

#### insight_pk *: str | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'insight_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.data.Log(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str)

Bases: [`Data`](#research_town.data.Data)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### profile_pk *: str*

#### timestep *: int*

### *class* research_town.data.MetaReview(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], proposal_pk: str | None = None, chair_pk: str | None = None, reviewer_pks: List[str] = [], author_pk: str | None = None, summary: str | None = None, strength: str | None = None, weakness: str | None = None, ethical_concerns: str | None = None, decision: bool = False, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### author_pk *: str | None*

#### chair_pk *: str | None*

#### decision *: bool*

#### ethical_concerns *: str | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'author_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'chair_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'content': FieldInfo(annotation=str, required=False, default=''), 'decision': FieldInfo(annotation=bool, required=False, default=False), 'ethical_concerns': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'reviewer_pks': FieldInfo(annotation=List[str], required=False, default=[]), 'strength': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'summary': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'weakness': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### proposal_pk *: str | None*

#### reviewer_pks *: List[str]*

#### strength *: str | None*

#### summary *: str | None*

#### weakness *: str | None*

### *class* research_town.data.MetaReviewWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, metareview_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### metareview_pk *: str*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'metareview_pk': FieldInfo(annotation=str, required=True), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.data.Paper(\*, pk: str = None, project_name: str | None = None, authors: List[str] = [], title: str, abstract: str, url: str | None = None, timestamp: int | None = None, sections: Dict[str, str] | None = None, table_captions: Dict[str, str] | None = None, figure_captions: Dict[str, str] | None = None, bibliography: Dict[str, str] | None = None, keywords: List[str] | None = None, domain: str | None = None, references: List[Dict[str, str]] | None = None, citation_count: int | None = 0, award: str | None = None, embed: Any | None = None)

Bases: [`Data`](#research_town.data.Data)

#### abstract *: str*

#### authors *: List[str]*

#### award *: str | None*

#### bibliography *: Dict[str, str] | None*

#### citation_count *: int | None*

#### domain *: str | None*

#### embed *: Any | None*

#### figure_captions *: Dict[str, str] | None*

#### keywords *: List[str] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'abstract': FieldInfo(annotation=str, required=True), 'authors': FieldInfo(annotation=List[str], required=False, default=[]), 'award': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'bibliography': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'citation_count': FieldInfo(annotation=Union[int, NoneType], required=False, default=0), 'domain': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'embed': FieldInfo(annotation=Union[Any, NoneType], required=False, default=None), 'figure_captions': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'keywords': FieldInfo(annotation=Union[List[str], NoneType], required=False, default=None), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'references': FieldInfo(annotation=Union[List[Dict[str, str]], NoneType], required=False, default=None), 'sections': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'table_captions': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'timestamp': FieldInfo(annotation=Union[int, NoneType], required=False, default=None), 'title': FieldInfo(annotation=str, required=True), 'url': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### references *: List[Dict[str, str]] | None*

#### sections *: Dict[str, str] | None*

#### table_captions *: Dict[str, str] | None*

#### timestamp *: int | None*

#### title *: str*

#### url *: str | None*

### *class* research_town.data.Profile(\*, pk: str = None, project_name: str | None = None, name: str, bio: str, collaborators: List[str] | None = [], institute: str | None = None, embed: Any | None = None, is_leader_candidate: bool | None = True, is_member_candidate: bool | None = True, is_reviewer_candidate: bool | None = True, is_chair_candidate: bool | None = True)

Bases: [`Data`](#research_town.data.Data)

#### bio *: str*

#### collaborators *: List[str] | None*

#### embed *: Any | None*

#### institute *: str | None*

#### is_chair_candidate *: bool | None*

#### is_leader_candidate *: bool | None*

#### is_member_candidate *: bool | None*

#### is_reviewer_candidate *: bool | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'bio': FieldInfo(annotation=str, required=True), 'collaborators': FieldInfo(annotation=Union[List[str], NoneType], required=False, default=[]), 'embed': FieldInfo(annotation=Union[Any, NoneType], required=False, default=None), 'institute': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'is_chair_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'is_leader_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'is_member_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'is_reviewer_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'name': FieldInfo(annotation=str, required=True), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### name *: str*

### *class* research_town.data.Progress(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [])

Bases: [`Data`](#research_town.data.Data)

#### content *: str*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* research_town.data.Proposal(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], q1: str | None = None, q2: str | None = None, q3: str | None = None, q4: str | None = None, q5: str | None = None, abstract: str = '', title: str | None = None, conference: str | None = None, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### abstract *: str*

#### conference *: str | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'abstract': FieldInfo(annotation=str, required=False, default=''), 'conference': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q1': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q2': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q3': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q4': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q5': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'title': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### q1 *: str | None*

#### q2 *: str | None*

#### q3 *: str | None*

#### q4 *: str | None*

#### q5 *: str | None*

#### title *: str | None*

### *class* research_town.data.ProposalWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, proposal_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=str, required=True), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### proposal_pk *: str*

### *class* research_town.data.Rebuttal(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], proposal_pk: str | None = None, reviewer_pk: str | None = None, author_pk: str | None = None, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### author_pk *: str | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'author_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'reviewer_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### proposal_pk *: str | None*

#### reviewer_pk *: str | None*

### *class* research_town.data.RebuttalWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, rebuttal_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'rebuttal_pk': FieldInfo(annotation=str, required=True), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### rebuttal_pk *: str*

### *class* research_town.data.Review(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], proposal_pk: str | None = None, reviewer_pk: str | None = None, summary: str | None = None, strength: str | None = None, weakness: str | None = None, ethical_concerns: str | None = None, score: int | None = None, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### ethical_concerns *: str | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'ethical_concerns': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'reviewer_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'score': FieldInfo(annotation=Union[int, NoneType], required=False, default=None), 'strength': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'summary': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'weakness': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### proposal_pk *: str | None*

#### reviewer_pk *: str | None*

#### score *: int | None*

#### strength *: str | None*

#### summary *: str | None*

#### weakness *: str | None*

### *class* research_town.data.ReviewWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, review_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'review_pk': FieldInfo(annotation=str, required=True), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### review_pk *: str*

## research_town.dbs.db_base module

### *class* research_town.dbs.db_base.BaseDB(data_class: Type[T], load_file_path: str | None = None)

Bases: `Generic`[`T`]

#### add(data: T) → None

#### delete(pk: str) → bool

#### get(\*\*conditions: str | int | float | List[int] | None) → List[T]

#### load_from_json(save_path: str, with_embed: bool = False, class_name: str | None = None) → None

#### load_from_pkl(save_path: str, class_name: str | None = None) → None

#### save_to_json(save_path: str, with_embed: bool = False, class_name: str | None = None) → None

#### save_to_pkl(save_path: str, class_name: str | None = None) → None

#### set_project_name(project_name: str) → None

#### update(pk: str, updates: Dict[str, Any]) → bool

## research_town.dbs.db_complex module

### *class* research_town.dbs.db_complex.ComplexDB(classes_to_register: List[Any], load_file_path: str | None = None)

Bases: `object`

#### add(data: T) → None

#### delete(data_class: Type[T], \*\*conditions: str | int | float) → int

#### get(data_class: Type[T], \*\*conditions: str | int | float) → List[T]

#### load_from_json(load_path: str, with_embed: bool = False) → None

#### load_from_pkl(load_path: str, with_embed: bool = False) → None

#### register_class(data_class: Any) → None

#### save_to_json(save_path: str, with_embed: bool = False) → None

#### save_to_pkl(save_path: str) → None

#### set_project_name(project_name: str) → None

#### update(data_class: Type[T], updates: Dict[str, Any], \*\*conditions: str | int | float) → int

## research_town.dbs.db_log module

### *class* research_town.dbs.db_log.LogDB(load_file_path: str | None = None)

Bases: [`ComplexDB`](#research_town.dbs.db_complex.ComplexDB)

## research_town.dbs.db_paper module

### *class* research_town.dbs.db_paper.PaperDB(load_file_path: str | None = None)

Bases: [`BaseDB`](#research_town.dbs.db_base.BaseDB)[[`Paper`](#research_town.data.Paper)]

#### match(query: str, papers: List[[Paper](#research_town.data.Paper)], num: int = 1) → List[[Paper](#research_town.data.Paper)]

#### pull_papers(num: int, domain: str) → None

#### transform_to_embed() → None

## research_town.dbs.db_profile module

### *class* research_town.dbs.db_profile.ProfileDB(load_file_path: str | None = None)

Bases: [`BaseDB`](#research_town.dbs.db_base.BaseDB)[[`Profile`](#research_town.data.Profile)]

#### match(query: str, profiles: List[[Profile](#research_town.data.Profile)], num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_chair_profiles(proposal: [Proposal](#research_town.data.Proposal), chair_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_leader_profiles(query: str, leader_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_member_profiles(leader: [Profile](#research_town.data.Profile), member_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_reviewer_profiles(proposal: [Proposal](#research_town.data.Proposal), reviewer_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### pull_profiles(agent_names: List[str], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → None

#### reset_role_availability() → None

#### search_profiles(condition: Dict[str, Any], query: str, num: int, update_fields: Dict[str, bool]) → List[[Profile](#research_town.data.Profile)]

#### transform_to_embed() → None

## research_town.dbs.db_progress module

### *class* research_town.dbs.db_progress.ProgressDB(load_file_path: str | None = None)

Bases: [`ComplexDB`](#research_town.dbs.db_complex.ComplexDB)

## Module contents

### *class* research_town.dbs.BaseDB(data_class: Type[T], load_file_path: str | None = None)

Bases: `Generic`[`T`]

#### add(data: T) → None

#### delete(pk: str) → bool

#### get(\*\*conditions: str | int | float | List[int] | None) → List[T]

#### load_from_json(save_path: str, with_embed: bool = False, class_name: str | None = None) → None

#### load_from_pkl(save_path: str, class_name: str | None = None) → None

#### save_to_json(save_path: str, with_embed: bool = False, class_name: str | None = None) → None

#### save_to_pkl(save_path: str, class_name: str | None = None) → None

#### set_project_name(project_name: str) → None

#### update(pk: str, updates: Dict[str, Any]) → bool

### *class* research_town.dbs.Idea(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### content *: str*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

### *class* research_town.dbs.IdeaBrainstormLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, idea_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### idea_pk *: str*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'idea_pk': FieldInfo(annotation=str, required=True), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### profile_pk *: str*

#### project_name *: str | None*

#### timestep *: int*

### *class* research_town.dbs.Insight(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### content *: str*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

### *class* research_town.dbs.LiteratureReviewLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, insight_pk: str | None = None)

Bases: [`Log`](#research_town.data.Log)

#### insight_pk *: str | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'insight_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### profile_pk *: str*

#### project_name *: str | None*

#### timestep *: int*

### *class* research_town.dbs.Log(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str)

Bases: [`Data`](#research_town.data.Data)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### profile_pk *: str*

#### project_name *: str | None*

#### timestep *: int*

### *class* research_town.dbs.LogDB(load_file_path: str | None = None)

Bases: [`ComplexDB`](#research_town.dbs.db_complex.ComplexDB)

### *class* research_town.dbs.MetaReview(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], proposal_pk: str | None = None, chair_pk: str | None = None, reviewer_pks: List[str] = [], author_pk: str | None = None, summary: str | None = None, strength: str | None = None, weakness: str | None = None, ethical_concerns: str | None = None, decision: bool = False, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### author_pk *: str | None*

#### chair_pk *: str | None*

#### content *: str*

#### decision *: bool*

#### ethical_concerns *: str | None*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'author_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'chair_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'content': FieldInfo(annotation=str, required=False, default=''), 'decision': FieldInfo(annotation=bool, required=False, default=False), 'ethical_concerns': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'reviewer_pks': FieldInfo(annotation=List[str], required=False, default=[]), 'strength': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'summary': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'weakness': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

#### proposal_pk *: str | None*

#### reviewer_pks *: List[str]*

#### strength *: str | None*

#### summary *: str | None*

#### weakness *: str | None*

### *class* research_town.dbs.MetaReviewWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, metareview_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### metareview_pk *: str*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'metareview_pk': FieldInfo(annotation=str, required=True), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### profile_pk *: str*

#### project_name *: str | None*

#### timestep *: int*

### *class* research_town.dbs.Paper(\*, pk: str = None, project_name: str | None = None, authors: List[str] = [], title: str, abstract: str, url: str | None = None, timestamp: int | None = None, sections: Dict[str, str] | None = None, table_captions: Dict[str, str] | None = None, figure_captions: Dict[str, str] | None = None, bibliography: Dict[str, str] | None = None, keywords: List[str] | None = None, domain: str | None = None, references: List[Dict[str, str]] | None = None, citation_count: int | None = 0, award: str | None = None, embed: Any | None = None)

Bases: [`Data`](#research_town.data.Data)

#### abstract *: str*

#### authors *: List[str]*

#### award *: str | None*

#### bibliography *: Dict[str, str] | None*

#### citation_count *: int | None*

#### domain *: str | None*

#### embed *: Any | None*

#### figure_captions *: Dict[str, str] | None*

#### keywords *: List[str] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'abstract': FieldInfo(annotation=str, required=True), 'authors': FieldInfo(annotation=List[str], required=False, default=[]), 'award': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'bibliography': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'citation_count': FieldInfo(annotation=Union[int, NoneType], required=False, default=0), 'domain': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'embed': FieldInfo(annotation=Union[Any, NoneType], required=False, default=None), 'figure_captions': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'keywords': FieldInfo(annotation=Union[List[str], NoneType], required=False, default=None), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'references': FieldInfo(annotation=Union[List[Dict[str, str]], NoneType], required=False, default=None), 'sections': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'table_captions': FieldInfo(annotation=Union[Dict[str, str], NoneType], required=False, default=None), 'timestamp': FieldInfo(annotation=Union[int, NoneType], required=False, default=None), 'title': FieldInfo(annotation=str, required=True), 'url': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

#### references *: List[Dict[str, str]] | None*

#### sections *: Dict[str, str] | None*

#### table_captions *: Dict[str, str] | None*

#### timestamp *: int | None*

#### title *: str*

#### url *: str | None*

### *class* research_town.dbs.PaperDB(load_file_path: str | None = None)

Bases: [`BaseDB`](#research_town.dbs.db_base.BaseDB)[[`Paper`](#research_town.data.Paper)]

#### match(query: str, papers: List[[Paper](#research_town.data.Paper)], num: int = 1) → List[[Paper](#research_town.data.Paper)]

#### pull_papers(num: int, domain: str) → None

#### transform_to_embed() → None

### *class* research_town.dbs.Profile(\*, pk: str = None, project_name: str | None = None, name: str, bio: str, collaborators: List[str] | None = [], institute: str | None = None, embed: Any | None = None, is_leader_candidate: bool | None = True, is_member_candidate: bool | None = True, is_reviewer_candidate: bool | None = True, is_chair_candidate: bool | None = True)

Bases: [`Data`](#research_town.data.Data)

#### bio *: str*

#### collaborators *: List[str] | None*

#### embed *: Any | None*

#### institute *: str | None*

#### is_chair_candidate *: bool | None*

#### is_leader_candidate *: bool | None*

#### is_member_candidate *: bool | None*

#### is_reviewer_candidate *: bool | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'bio': FieldInfo(annotation=str, required=True), 'collaborators': FieldInfo(annotation=Union[List[str], NoneType], required=False, default=[]), 'embed': FieldInfo(annotation=Union[Any, NoneType], required=False, default=None), 'institute': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'is_chair_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'is_leader_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'is_member_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'is_reviewer_candidate': FieldInfo(annotation=Union[bool, NoneType], required=False, default=True), 'name': FieldInfo(annotation=str, required=True), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### name *: str*

#### pk *: str*

#### project_name *: str | None*

### *class* research_town.dbs.ProfileDB(load_file_path: str | None = None)

Bases: [`BaseDB`](#research_town.dbs.db_base.BaseDB)[[`Profile`](#research_town.data.Profile)]

#### match(query: str, profiles: List[[Profile](#research_town.data.Profile)], num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_chair_profiles(proposal: [Proposal](#research_town.data.Proposal), chair_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_leader_profiles(query: str, leader_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_member_profiles(leader: [Profile](#research_town.data.Profile), member_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### match_reviewer_profiles(proposal: [Proposal](#research_town.data.Proposal), reviewer_num: int = 1) → List[[Profile](#research_town.data.Profile)]

#### pull_profiles(agent_names: List[str], config: [Config](research_town.configs.md#research_town.configs.config.Config)) → None

#### reset_role_availability() → None

#### search_profiles(condition: Dict[str, Any], query: str, num: int, update_fields: Dict[str, bool]) → List[[Profile](#research_town.data.Profile)]

#### transform_to_embed() → None

### *class* research_town.dbs.Progress(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [])

Bases: [`Data`](#research_town.data.Data)

#### content *: str*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

### *class* research_town.dbs.ProgressDB(load_file_path: str | None = None)

Bases: [`ComplexDB`](#research_town.dbs.db_complex.ComplexDB)

### *class* research_town.dbs.Proposal(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], q1: str | None = None, q2: str | None = None, q3: str | None = None, q4: str | None = None, q5: str | None = None, abstract: str = '', title: str | None = None, conference: str | None = None, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### abstract *: str*

#### conference *: str | None*

#### content *: str*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'abstract': FieldInfo(annotation=str, required=False, default=''), 'conference': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q1': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q2': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q3': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q4': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'q5': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'title': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

#### q1 *: str | None*

#### q2 *: str | None*

#### q3 *: str | None*

#### q4 *: str | None*

#### q5 *: str | None*

#### title *: str | None*

### *class* research_town.dbs.ProposalWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, proposal_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=str, required=True), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### profile_pk *: str*

#### project_name *: str | None*

#### proposal_pk *: str*

#### timestep *: int*

### *class* research_town.dbs.Rebuttal(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], proposal_pk: str | None = None, reviewer_pk: str | None = None, author_pk: str | None = None, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### author_pk *: str | None*

#### content *: str*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'author_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'content': FieldInfo(annotation=str, required=False, default=''), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'reviewer_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

#### proposal_pk *: str | None*

#### reviewer_pk *: str | None*

### *class* research_town.dbs.RebuttalWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, rebuttal_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'rebuttal_pk': FieldInfo(annotation=str, required=True), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### profile_pk *: str*

#### project_name *: str | None*

#### rebuttal_pk *: str*

#### timestep *: int*

### *class* research_town.dbs.Review(\*, pk: str = None, project_name: str | None = None, content: str = '', eval_score: List[int] | None = [], proposal_pk: str | None = None, reviewer_pk: str | None = None, summary: str | None = None, strength: str | None = None, weakness: str | None = None, ethical_concerns: str | None = None, score: int | None = None, \*\*extra_data: Any)

Bases: [`Progress`](#research_town.data.Progress)

#### content *: str*

#### ethical_concerns *: str | None*

#### eval_score *: List[int] | None*

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=   'extra': 'allow'  *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'content': FieldInfo(annotation=str, required=False, default=''), 'ethical_concerns': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'eval_score': FieldInfo(annotation=Union[List[int], NoneType], required=False, default=[]), 'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'proposal_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'reviewer_pk': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'score': FieldInfo(annotation=Union[int, NoneType], required=False, default=None), 'strength': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'summary': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'weakness': FieldInfo(annotation=Union[str, NoneType], required=False, default=None)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### project_name *: str | None*

#### proposal_pk *: str | None*

#### reviewer_pk *: str | None*

#### score *: int | None*

#### strength *: str | None*

#### summary *: str | None*

#### weakness *: str | None*

### *class* research_town.dbs.ReviewWritingLog(\*, pk: str = None, project_name: str | None = None, timestep: int = 0, profile_pk: str, review_pk: str)

Bases: [`Log`](#research_town.data.Log)

#### model_computed_fields *: ClassVar[dict[str, ComputedFieldInfo]]* *=     *

A dictionary of computed field names and their corresponding ComputedFieldInfo objects.

#### model_config *: ClassVar[ConfigDict]* *=     *

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *=   'pk': FieldInfo(annotation=str, required=False, default_factory= lambda ), 'profile_pk': FieldInfo(annotation=str, required=True), 'project_name': FieldInfo(annotation=Union[str, NoneType], required=False, default=None), 'review_pk': FieldInfo(annotation=str, required=True), 'timestep': FieldInfo(annotation=int, required=False, default=0)  *

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### pk *: str*

#### profile_pk *: str*

#### project_name *: str | None*

#### review_pk *: str*

#### timestep *: int*
