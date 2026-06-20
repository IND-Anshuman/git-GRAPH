from typing import Protocol, runtime_checkable

@runtime_checkable
class IDecisionAdvisor(Protocol): ...

@runtime_checkable
class IIntentAdvisor(Protocol): ...

@runtime_checkable
class ICausalAdvisor(Protocol): ...
