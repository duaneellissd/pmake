'''
What is a "nested_dict"?

This is very simular to: 'benadict' - but I choose not to use that system
because it is massively full of bloat so I reject it.

This supports or is effectively a dictionary wihtin a dictionary within a dictionary

For example:   thing.set("foo.bar.cat",1234)
   is the same as a Python dictionary like this:
    { "foo" : { "bar: { "cat" : 1234 }}}

Each dotted element creates another nesting layer in the nested dictionary.

Thus it is very/quit recursive.

'''
from .nested_dict import NestedDict
from .nested_dict import NestedDict_KeyError
