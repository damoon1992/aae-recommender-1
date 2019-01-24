import torch
import torch.nn as nn

from torch import optim

from abc import ABC, abstractmethod
from collections import OrderedDict
import torch

"""
Key idea: The conditions we pass through all the code
could be a list of (name, condition_obj) tuples.
Each condition_obj has an interface to encode a batch
and (optional) to update its parameters wrt (global) ae loss.


"""


class ConditionList(OrderedDict):
    """
    Condition list is an ordered dict with attribute names as keys and
    condition instances as values.
    Order is meaningful.
    It subclasses OrderedDict.
    """

    def __init__(self, items):
        super(ConditionList, self).__init__(items)
        assert all(isinstance(v, ConditionBase) for v in self.values())

    def encode_impose(self, x, condition_inputs):
        assert len(condition_inputs) == len(self)
        for condition, condition_input in zip(self.values(), condition_inputs):
            x = condition.encode_impose(x, condition_input)
        return x

    def zero_grad(self):
        """ Forward the zero_grad call to all conditions in list
        such they can reset their gradients """
        for condition in self.values():
            condition.zero_grad()
        return self

    def step(self):
        """ Forward the step call to all conditions in list,
        such that these can update their individual parameters"""
        for condition in self.values():
            condition.step()
        return self

    def size_increment(self):
        """ Aggregates sizes from various conditions
        for convenience use in determining decoder properties
        """
        return sum(v.size_increment() for v in self.values())


class ConditionBase(ABC):
    """ Abstract Base Class for a generic condition """

    #####################################################################
    # Condition supplies info how much it will increment the size of data
    # Some conditions might want to prepare on whole dataset .
    # eg to build a vocabulary and compute global IDF and stuff
    def prepare(self, raw_inputs):
        """ Prepares the condition wrt to the whole raw data for the condition
        To be called *once* on the whole (condition)-data.
        """
        return self

    # Latest after preparing, size_increment should yield reasonable results.
    @abstractmethod
    def size_increment(self):
        """ Returns the output dimension of the condition,
        such that: 
        unconditioned.size(1) + condition.size_increment() = conditioned.size(1)
        Note that for additive or multiplicative conditions, dim should be zero.
        """
    #####################################################################

    ###########################################################################
    # Condition can encode the raw input and knows how to impose itself to data
    @abstractmethod
    def encode(self, input):
        """ Encodes the input for the condition """

    @abstractmethod
    def impose(self, input, encoded_condition):
        """ Applies the condition, for instance by concatenation.
        Could also use multiplicative or additive conditioning.
        """

    def encode_impose(self, input, condition_input):
        """ First encodes `condition_input`, then applies condition to `input`.
        """
        return self.impose(input, self.encode(condition_input))
    ###########################################################################

    ################################################
    # Condition knows how to optimize own parameters
    def zero_grad(self):
        """
        Clear out gradients.
        Per default does nothing on step (optional for subclasses to implement.
        To be called before each batch.
        """
        return self

    def step(self):
        """
        Update condition's associated parameters.
        Per default does nothing on step (optional for subclasses to implement.

        To be called after each batch.
        """
        return self
    ################################################



    @classmethod
    def __subclasshook__(cls, C):
        if cls is ConditionBase:
            # Check if abstract parts of interface are satisified
            mro = C.__mro__
            if any("encode" in B.__dict__ for B in mro) \
                    and any("impose" in B.__dict__ for B in mro) \
                    and any("size_increment" in B.__dict__ for B in mro):
                return True
        return NotImplemented  # Proceed with usual mechanisms



""" Three basic variants of conditioning
1. Concatenation-based conditioning
2. Conditional biasing
3. Conditional scaling
See also: https://distill.pub/2018/feature-wise-transformations/

Condition implementations should subclass one of the following three baseclasses.
"""


class ConcatenationBasedConditioning(ConditionBase):
    # Subclasses still need to specify .size_increment()
    # as concatenation based
    dim = 1
    def impose(self, input, encoded_condition):
        return torch.cat([input, encoded_condition], dim=self.dim)


class ConditionalBiasing(ConditionBase):
    def impose(self, input, encoded_condition):
        return input + encoded_condition

    def size_increment(self):
        return 0


class ConditionalScaling(ConditionBase):
    def impose(self, input, encoded_condition):
        return input * encoded_condition

    def size_increment(self):
        return 0


# class PretrainedWordEmbeddingCondition(ConcatenationBasedConditioning):
#     def __init__(self, gensim_embedding, **tfidf_params):
#         super().__init__()
#         self.vect = EmbeddedVectorizer(embedding, **self.tfidf_params)

#     def encode(self, input):
#         return self.vect.fit_transform(input)

#     def step(self):
#         pass


class EmbeddingBagCondition(ConcatenationBasedConditioning):

    """ A condition with a *trainable* embedding bag.
    It is suited for conditioning on categorical variables.
    >>> cc = EmbeddingBagCondition(100,10)
    >>> cc
    EmbeddingBagCondition(
      (embedding_bag): EmbeddingBag(100, 10, mode=mean)
    )
    >>> issubclass(EmbeddingBagCondition, ConditionBase)
    True
    >>> isinstance(cc, ConditionBase)
    True
    """

    def __init__(self, num_embeddings, embedding_dim, **kwargs):
        """TODO: to be defined1. """
        nn.Module.__init__(self)

        self.embedding_bag = nn.EmbeddingBag(num_embeddings,
                                             embedding_dim,
                                             **kwargs)

        # register this module's parameters with the optimizer
        self.optimizer = optim.Adam(self.embedding_bag.parameters())
        self.output_dim = embedding_dim

    def encode(self, input):
        return self.embedding_bag(input)

    def zero_grad(self):
        self.optimizer.zero_grad()

    def step(self):
        # loss.backward() to be called before by client (such as in ae_step)
        # The condition object can update its own parameters wrt global loss
        self.optimizer.step()

    def size_increment(self):
        return self.output_dim
