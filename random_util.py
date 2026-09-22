from random import randint
from typing import Literal, Callable
from collections.abc import MutableSequence, Sequence, Collection, Iterator
from helpers.misc_util import is_hashable_seq

class EmptySequenceError(Exception): pass
class NotEnoughElementsError(Exception): pass
class RemoveNotPermittedError(Exception): pass

# -----------------------------------------------------------

class ValidationOptions:

    '''
    USAGE:
    - turn off validation: `ValidationOptions()`
    or more explicitly `ValidationOptions().disable_all()`
    - validate everything: **don't supply the `validation_options` argument for**
    `sample_from_sequence()` (unless `default_validation_options` has been changed)
    or more explicitly `ValidationOptions().validate_all()`
    - opt in to a few: `ValidationOptions(check_blah = True)`
    or `ValidationOptions().disable_all_except(check_blah = True)`
    - opt out of a few: `ValidationOptions().validate_all_except(check_blah = False)`

    Note that you can change the default `validation_options` for `sample_from_sequence()`
    by setting `random_util.default_validation_options`
    to `lambda: ValidationOptions(whatever_you_want)`.
    '''

    def __init__(
        self,
        check_not_negative_count: bool = False,
        check_valid_mode: bool = False,
        check_seq_is_mutable: bool = False,
        check_seq_not_empty: bool = False,
        check_enough_elements: bool = False
    ) -> None:
        self.check_not_negative_count: bool = check_not_negative_count
        self.check_valid_mode: bool = check_valid_mode
        self.check_seq_is_mutable: bool = check_seq_is_mutable
        self.check_seq_not_empty: bool = check_seq_not_empty
        self.check_enough_elements: bool = check_enough_elements

    def validate_all(self) -> ValidationOptions:
        self.check_not_negative_count = True
        self.check_valid_mode = True
        self.check_seq_is_mutable = True
        self.check_seq_not_empty = True
        self.check_enough_elements = True
        return self

    def disable_all(self) -> ValidationOptions:
        self.check_not_negative_count = False
        self.check_valid_mode = False
        self.check_seq_is_mutable = False
        self.check_seq_not_empty = False
        self.check_enough_elements = False
        return self

    def validate_all_except(
        self,
        check_not_negative_count: bool = True,
        check_valid_mode: bool = True,
        check_seq_is_mutable: bool = True,
        check_seq_not_empty: bool = True,
        check_enough_elements: bool = True
    ) -> ValidationOptions:
        self.check_not_negative_count = check_not_negative_count
        self.check_valid_mode = check_valid_mode
        self.check_seq_is_mutable = check_seq_is_mutable
        self.check_seq_not_empty = check_seq_not_empty
        self.check_enough_elements = check_enough_elements
        return self

    def disable_all_except(
        self,
        check_not_negative_count: bool = False,
        check_valid_mode: bool = False,
        check_seq_is_mutable: bool = False,
        check_seq_not_empty: bool = False,
        check_enough_elements: bool = False
    ) -> ValidationOptions:
        self.check_not_negative_count = check_not_negative_count
        self.check_valid_mode = check_valid_mode
        self.check_seq_is_mutable = check_seq_is_mutable
        self.check_seq_not_empty = check_seq_not_empty
        self.check_enough_elements = check_enough_elements
        return self

default_validation_options: Callable[[], ValidationOptions] = \
    lambda: ValidationOptions().validate_all()

# -----------------------------------------------------------

class Exclusion[T]:

    def __init__(
        self,
        elements_to_exclude: Collection[T] = (),
        use_rejection: bool = False
    ) -> None:
        self.elements_to_exclude: Collection[T] = elements_to_exclude
        self.use_rejection: bool = use_rejection
        self.seq_with_exclusion: Sequence[T] = ()
        self.new_to_old_index_map: dict[int, int] = {}

    def initialize(self, seq: Sequence[T]) -> None:
        self.seq_with_exclusion = ()
        self.new_to_old_index_map = {}
        if not self.use_rejection and len(self.elements_to_exclude) > 0:
            kept_indices_and_elements: Iterator[tuple[int, ...] | tuple[T, ...]] = zip(
                *((i, e) for i, e in enumerate(seq) if e not in self.elements_to_exclude)
            )
            try:
                self.new_to_old_index_map = {
                    new_index: old_index for new_index, old_index
                    in enumerate(next(kept_indices_and_elements))
                }
                self.seq_with_exclusion = next(kept_indices_and_elements)
            except StopIteration:
                pass
        else:
            self.seq_with_exclusion = seq

    def is_element_excluded(self, element: T) -> bool:
        if self.use_rejection:
            return element in self.elements_to_exclude
        else:
            return False

    def get_old_indices(self, new_indices: set[int]) -> set[int]:
        if len(self.new_to_old_index_map) == 0:
            return new_indices
        return {self.new_to_old_index_map[index] for index in new_indices}

    def get_seq_with_exclusion(self, cheap: bool = False) -> Sequence[T]:
        if cheap or not self.use_rejection or len(self.elements_to_exclude) == 0:
            return self.seq_with_exclusion
        return [
            element for element in self.seq_with_exclusion
            if element not in self.elements_to_exclude
        ]

# -----------------------------------------------------------

class IndexManager[T]:

    def __init__(
        self,
        seq: Sequence[T],
        mode: Literal["with_replacement", "distinct_indices", "unique_elements"],
        use_rejection_on_already_added: bool,
        use_coarse_hashability_check: bool
    ) -> None:
        self.seq: Sequence[T] = seq
        self.mode: Literal["with_replacement", "distinct_indices", "unique_elements"] = mode
        self.use_rejection_on_already_added: bool = use_rejection_on_already_added
        self.random_indices: set[int] = set()
        self.eligible_indices: list[int] | None = (
            None if use_rejection_on_already_added or mode == "with_replacement"
            else list(range(len(seq)))
        )
        self.random_elements: set[T] | list[T] | None = (
            None if not use_rejection_on_already_added or mode != "unique_elements"
            else (
                set() if is_hashable_seq(seq, use_coarse_hashability_check)
                else []
            )
        )
        self.random_pos: int | None = None
        self.random_index: int = -1

    def sample_element(self) -> T:
        if self.eligible_indices is None:
            self.random_index = randint(0, len(self.seq) - 1)
        else:
            self.random_pos = randint(0, len(self.eligible_indices) - 1)
            self.random_index = self.eligible_indices[self.random_pos]
        return self.seq[self.random_index]

    def is_index_excluded(self) -> bool:
        if self.mode == "with_replacement":
            return False
        elif self.mode == "distinct_indices":
            if self.use_rejection_on_already_added:
                return self.random_index in self.random_indices
            else:
                return False
        elif self.mode == "unique_elements":
            if self.use_rejection_on_already_added:
                assert self.random_elements is not None
                return self.seq[self.random_index] in self.random_elements
            else:
                return False
        else:
            raise RuntimeError("code should never reach here")

    def update_data_structures(self) -> None:
        self.random_indices.add(self.random_index)
        if self.mode == "distinct_indices" and not self.use_rejection_on_already_added:
            assert self.eligible_indices is not None
            assert self.random_pos is not None
            self.eligible_indices[self.random_pos] = self.eligible_indices[-1]
            self.eligible_indices.pop()
            self.random_pos = None
        elif self.mode == "unique_elements":
            if self.use_rejection_on_already_added:
                assert self.random_elements is not None
                if isinstance(self.random_elements, set):
                    self.random_elements.add(self.seq[self.random_index])
                else:
                    self.random_elements.append(self.seq[self.random_index])
            else:
                assert self.eligible_indices is not None
                self.eligible_indices = [
                    index for index in self.eligible_indices
                    if self.seq[index] != self.seq[self.random_index]
                ]

# -----------------------------------------------------------

def validate_args[T](
    validation_options: ValidationOptions,
    exclude: Exclusion[T],
    count: int,
    remove: bool,
    mode: Literal["with_replacement", "distinct_indices", "unique_elements"],
    seq_is_mutable: bool,
    use_coarse_hashability_check: bool,
    cheap_coarse_exclusion_validation: bool
) -> None:

    seq_with_exclusion: Sequence[T] | None = None
    def get_seq_with_exclusion() -> Sequence[T]:
        nonlocal seq_with_exclusion
        if seq_with_exclusion is None:
            seq_with_exclusion = exclude.get_seq_with_exclusion(cheap_coarse_exclusion_validation)
        return seq_with_exclusion
    
    if validation_options.check_not_negative_count and count < 0:
        raise ValueError("count should not be negative")
    
    if validation_options.check_valid_mode and mode not in [
        "with_replacement", "distinct_indices", "unique_elements"
    ]:
        raise ValueError("unrecognized mode; check the type annotation")
    
    if validation_options.check_seq_is_mutable and remove and not seq_is_mutable:
        raise RemoveNotPermittedError("cannot remove elements from immutable sequence")

    if validation_options.check_seq_not_empty and len(get_seq_with_exclusion()) == 0 and count > 0:
        raise EmptySequenceError("cannot sample from an empty sequence (after exclusion)")
    
    if (
        validation_options.check_enough_elements
        and mode == "distinct_indices"
        and len(get_seq_with_exclusion()) < count
    ):
        raise NotEnoughElementsError("not enough distinct eligible indices (after exclusion)")
    
    if validation_options.check_enough_elements and mode == "unique_elements":
        deduplicated: Collection[T] = (
            set(get_seq_with_exclusion())
            if is_hashable_seq(get_seq_with_exclusion(), use_coarse_hashability_check)
            else [
                e for i, e in enumerate(get_seq_with_exclusion())
                if e not in get_seq_with_exclusion()[:i]
            ]
        )
        if len(deduplicated) < count:
            raise NotEnoughElementsError("not enough unique eligible elements (after exclusion)")

# -----------------------------------------------------------

def sample_from_sequence[T](
    seq: Sequence[T],
    count: int = 1,
    remove: bool = False,
    exclude: Exclusion[T] | None = None,
    mode: Literal["with_replacement", "distinct_indices", "unique_elements"] = "with_replacement",
    use_rejection_on_already_added: bool = False,
    use_coarse_hashability_check: bool = False,
    validation_options: ValidationOptions | None = None,
    cheap_coarse_exclusion_validation: bool = False
) -> list[T]:

    if exclude is None:
        exclude = Exclusion()
    if validation_options is None:
        validation_options = default_validation_options()

    exclude.initialize(seq)
    validate_args(
        validation_options, exclude, count,
        remove, mode, isinstance(seq, MutableSequence),
        use_coarse_hashability_check, cheap_coarse_exclusion_validation
    )

    final_result: list[T] = []
    index_manager: IndexManager[T] = IndexManager(
        exclude.seq_with_exclusion, mode, use_rejection_on_already_added,
        use_coarse_hashability_check
    )

    while len(final_result) < count:
        element: T = index_manager.sample_element()
        if not exclude.is_element_excluded(element) and not index_manager.is_index_excluded():
            final_result.append(element)
            index_manager.update_data_structures()

    if remove:
        assert isinstance(seq, MutableSequence)
        indices_to_delete: set[int] = exclude.get_old_indices(index_manager.random_indices)
        temp_seq: list[T] = []
        for i, element in enumerate(seq):
            if i not in indices_to_delete:
                temp_seq.append(element)
        seq.clear()
        seq.extend(temp_seq)
            
    return final_result