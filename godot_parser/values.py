"""The grammar of low-level values in the GD file format"""

from pyparsing import (
    DelimitedList,
    Forward,
    Group,
    Keyword,
    Opt,
    QuotedString,
    Suppress,
    Word,
    alphanums,
    alphas,
    common,
)

from .objects import GDObject, StringName

boolean = (
    (Keyword("true") | Keyword("false"))
    .set_name("bool")
    .set_parse_action(lambda x: x[0].lower() == "true")
)

null = Keyword("null").set_parse_action(lambda _: [None])

_string = QuotedString('"', escChar="\\", multiline=True).set_name("string")

_string_name = (
    Suppress('&') + _string
).set_name("string_name").set_parse_action(StringName.from_parser)

primitive = (
    null | _string | _string_name | boolean | common.number
)
value = Forward()

# Vector2( 1, 2 )
obj_type = (
    Word(alphas, alphanums).set_results_name("object_name")
    + Suppress("(")
    + DelimitedList(value)
    + Suppress(")")
).set_parse_action(GDObject.from_parser)

# [ 1, 2 ] or [ 1, 2, ]
list_ = (
    Group(
        Suppress("[") + Opt(DelimitedList(value)) + Opt(Suppress(",")) + Suppress("]")
    )
    .set_name("list")
    .set_parse_action(lambda p: p.as_list())
)
key_val = Group(QuotedString('"', escChar="\\") + Suppress(":") + value)

# {
# "_edit_use_anchors_": false
# }
dict_ = (
    (Suppress("{") + Opt(DelimitedList(key_val)) + Suppress("}"))
    .set_name("dict")
    .set_parse_action(lambda d: {k: v for k, v in d})
)

# Exports

value <<= primitive | list_ | dict_ | obj_type
