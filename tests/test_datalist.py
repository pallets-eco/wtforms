import pytest

from tests.common import DummyPostData
from wtforms import Choice
from wtforms import DataList
from wtforms import EmailField
from wtforms import FieldList
from wtforms import Form
from wtforms import FormField
from wtforms import StringField


class StrForm(Form):
    tag = StringField(datalist=DataList(["python", "htmx", "wtforms"]))


class ChoiceForm(Form):
    country = StringField(
        datalist=DataList(
            choices=[Choice("FR", "France"), Choice("US", "United States")]
        )
    )


def test_str_choices_render_options():
    """String choices render as ``<option value="...">`` inside ``<datalist>``."""
    form = StrForm()
    html = str(form.tag.datalist())
    assert '<datalist id="tag-datalist">' in html
    assert '<option value="python">' in html
    assert '<option value="htmx">' in html
    assert '<option value="wtforms">' in html


def test_choice_choices_render_value_and_label():
    """``Choice`` instances render both ``value=`` and ``label=`` attributes."""
    form = ChoiceForm()
    html = str(form.country.datalist())
    assert 'value="FR"' in html
    assert 'label="France"' in html
    assert 'value="US"' in html
    assert 'label="United States"' in html


@pytest.mark.parametrize(
    ("postdata", "expected"),
    [
        pytest.param(DummyPostData({"query": ["hello"]}), "hello", id="with-data"),
        pytest.param(None, "default", id="data-is-none"),
    ],
)
def test_callable_choices_receives_form_and_field(postdata, expected):
    """A callable ``DataList`` is invoked with ``(form, field)`` — its
    ``field.data`` (or ``None`` when no value is bound) drives the result."""

    class F(Form):
        query = StringField(
            datalist=DataList(lambda form, field: [f"{field.data or 'default'}-x"])
        )

    html = str(F(postdata).query.datalist())
    assert f'<option value="{expected}-x">' in html


def test_zero_arg_callable_choices():
    """A 0-argument callable is allowed (lazy constant)."""
    calls = {"n": 0}

    def suggest():
        calls["n"] += 1
        return ["FR", "DE"]

    class F(Form):
        country = StringField(datalist=DataList(suggest))

    html = str(F().country.datalist())
    assert '<option value="FR">' in html
    assert '<option value="DE">' in html
    assert calls["n"] >= 1


def test_field_without_datalist_has_no_list_attr():
    """A field with no ``datalist=`` does not emit a ``list=`` attribute."""

    class F(Form):
        x = StringField()

    form = F()
    assert "list=" not in form.x()


def test_string_reference_emits_list_attr():
    """``datalist="some-id"`` emits ``list="some-id"`` on the input."""

    class F(Form):
        field = StringField(datalist="external")

    form = F()
    assert 'list="external"' in form.field()


def test_field_datalist_empty_for_string_ref():
    """``field.datalist()`` returns empty markup for string references."""

    class F(Form):
        x = StringField(datalist="external")

    form = F()
    assert str(form.x.datalist()) == ""


def test_field_datalist_empty_when_absent():
    """``field.datalist()`` returns empty markup when no ``datalist=``."""

    class F(Form):
        x = StringField()

    form = F()
    assert str(form.x.datalist()) == ""


def test_inline_datalist_form_prefix_propagates():
    """Inline DataList id includes the form prefix via the field id."""

    class F(Form):
        country = StringField(datalist=DataList(["FR"]))

    form = F(prefix="signup")
    assert form.country._datalist.id == "signup-country-datalist"
    assert 'list="signup-country-datalist"' in form.country()


def test_inline_datalist_in_fieldlist_unique_ids_per_entry():
    """Each FieldList entry gets its own DataList clone with a unique id."""

    class F(Form):
        items = FieldList(
            StringField(datalist=DataList(["a", "b"])),
            min_entries=3,
        )

    form = F()
    ids = [entry._datalist.id for entry in form.items]
    assert ids == ["items-0-datalist", "items-1-datalist", "items-2-datalist"]
    for entry in form.items:
        assert f'list="{entry._datalist.id}"' in entry()


def test_inline_datalist_in_fieldlist_renders_per_entry():
    """``entry()`` emits the input only; ``entry.datalist()`` renders each
    entry's own ``<datalist>``."""

    class F(Form):
        items = FieldList(
            StringField(datalist=DataList(["a", "b"])),
            min_entries=2,
        )

    form = F()
    for i, entry in enumerate(form.items):
        input_html = str(entry())
        assert f'list="items-{i}-datalist"' in input_html
        assert "<datalist" not in input_html
        dl_html = str(entry.datalist())
        assert f'<datalist id="items-{i}-datalist">' in dl_html


def test_inline_callable_datalist_per_fieldlist_entry():
    """A callable inline DataList receives each entry's own data at render."""

    class F(Form):
        items = FieldList(
            StringField(
                datalist=DataList(
                    choices=lambda form, field: [
                        f"{field.data}-1",
                        f"{field.data}-2",
                    ]
                )
            ),
            min_entries=2,
        )

    form = F(data={"items": ["foo", "bar"]})
    dl0 = str(form.items[0].datalist())
    dl1 = str(form.items[1].datalist())
    assert '<option value="foo-1">' in dl0
    assert '<option value="bar-1">' in dl1


def test_inline_datalist_in_formfield_subform():
    """An inline DataList inside a FormField sub-form gets a prefixed id."""

    class Sub(Form):
        inner = StringField(datalist=DataList(["z"]))

    class F(Form):
        sub = FormField(Sub)

    form = F()
    assert form.sub.inner._datalist.id == "sub-inner-datalist"
    assert 'list="sub-inner-datalist"' in form.sub.inner()


def test_email_field_compatible():
    """``EmailField`` (a text-based input) accepts ``datalist=`` and emits ``list=``."""

    class F(Form):
        email = EmailField(datalist=DataList(["alice@example.com"]))

    html = F().email()
    assert 'list="email-datalist"' in html


def test_render_kw_on_datalist():
    """``render_kw`` on a ``DataList`` is applied as attributes on ``<datalist>``."""

    class F(Form):
        x = StringField(datalist=DataList(["a"], render_kw={"data-foo": "bar"}))

    html = str(F().x.datalist())
    assert 'data-foo="bar"' in html


def test_choice_render_kw_on_option():
    """``render_kw`` on a ``Choice`` is applied as attributes on its ``<option>``."""

    class F(Form):
        x = StringField(datalist=DataList([Choice("x", render_kw={"disabled": True})]))

    html = str(F().x.datalist())
    assert "disabled" in html


def test_none_choices_renders_empty_datalist():
    """``choices=None`` renders an empty ``<datalist>`` with no options."""

    class F(Form):
        x = StringField(datalist=DataList(None))

    html = str(F().x.datalist())
    assert html == '<datalist id="x-datalist"></datalist>'


@pytest.mark.parametrize(
    ("choices", "data", "selected"),
    [
        pytest.param(
            [Choice("FR", "France"), Choice("US", "United States")],
            {"country": "FR"},
            ["FR"],
            id="static-match",
        ),
        pytest.param(
            [Choice("FR"), Choice("US")],
            None,
            [],
            id="no-data-no-flag",
        ),
        pytest.param(
            lambda form, field: [Choice("FR")] if field.data == "FR" else [],
            {"country": "FR"},
            ["FR"],
            id="callable-match",
        ),
    ],
)
def test_iter_choices_flags_selected(choices, data, selected):
    """``iter_choices(field)`` flags Choices whose value matches ``field.data``."""

    class F(Form):
        country = StringField(datalist=DataList(choices))

    form = F(data=data) if data else F()
    flagged = [
        c.value
        for c in form.country._datalist.iter_choices(form.country)
        if c._selected
    ]
    assert flagged == selected


def test_widget_replaces_default_rendering():
    """A custom ``widget`` callable replaces the default ``<datalist>`` markup."""

    def listbox_widget(datalist, field=None, **kwargs):
        items = "".join(
            f'<li role="option">{c.value}</li>' for c in datalist.iter_choices(field)
        )
        return f'<ul role="listbox" id="{datalist.id}">{items}</ul>'

    class F(Form):
        suggestions = StringField(datalist=DataList(["a", "b"], widget=listbox_widget))

    html = str(F().suggestions.datalist())
    assert html == (
        '<ul role="listbox" id="suggestions-datalist">'
        '<li role="option">a</li><li role="option">b</li>'
        "</ul>"
    )
    assert "<datalist" not in html


def test_widget_receives_field_for_callable_choices():
    """The widget is invoked with the bound ``field`` kwarg, so callable
    choices receive the same field instance."""

    seen = {}

    def widget(datalist, field=None, **kwargs):
        seen["field"] = field
        return "<ok>"

    class F(Form):
        query = StringField(
            datalist=DataList(
                choices=lambda form, field: [f"{field.data}-x"],
                widget=widget,
            )
        )

    form = F(data={"query": "hello"})
    out = form.query._datalist(field=form.query)
    assert out == "<ok>"
    assert seen["field"] is form.query


def test_widget_preserved_through_clone():
    """A custom widget on the inline DataList survives the per-field clone."""

    def widget(datalist, field=None, **kwargs):
        return f"<custom id={datalist.id}>"

    class F(Form):
        items = StringField(datalist=DataList(["x"], widget=widget))

    form = F()
    assert str(form.items.datalist()) == "<custom id=items-datalist>"


def test_render_kwargs_passed_to_datalist_attributes():
    """Caller kwargs are emitted as HTML attributes on ``<datalist>``,
    identically to :meth:`Field.__call__ <wtforms.fields.Field.__call__>`."""

    class F(Form):
        tag = StringField(datalist=DataList(["a"]))

    html = str(F().tag.datalist(class_="suggestions", data_role="autocomplete"))
    assert "<datalist " in html
    assert 'class="suggestions"' in html
    assert 'data-role="autocomplete"' in html


def test_render_kwargs_override_render_kw():
    """Caller kwargs override ``render_kw`` defined on the DataList."""

    class F(Form):
        x = StringField(datalist=DataList(["a"], render_kw={"class": "default"}))

    html = str(F().x.datalist(class_="custom"))
    assert 'class="custom"' in html
    assert 'class="default"' not in html


def test_default_widget_is_datalist_widget():
    """:class:`DataList` defaults to :class:`~wtforms.widgets.DataListWidget`."""
    from wtforms.widgets import DataListWidget

    assert isinstance(DataList.widget, DataListWidget)
    dl = DataList(["a"])
    assert isinstance(dl.widget, DataListWidget)
