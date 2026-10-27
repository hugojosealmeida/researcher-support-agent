"""Abstract base class for all pipeline agents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from research_pipeline.state import PipelineState


class PipelineAgent(ABC):
    """Every pipeline phase implements this interface.

    Attributes
    ----------
    name : str
        Unique identifier used by the pipeline to invoke the agent
        (e.g. ``"planning"``, ``"literature_search"``).
    """

    name: str  # set by subclasses

    @abstractmethod
    def run(self, state: PipelineState) -> PipelineState:
        """Execute the agent logic and return the updated state.

        Subclasses may mutate *state* in-place and must also return it
        so the pipeline can verify the reference hasn't changed.
        """
        ...
