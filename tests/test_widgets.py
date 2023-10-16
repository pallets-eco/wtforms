import pytest
from markupsafe import Markup

from wtforms.widgets.core import CheckboxInput
from wtforms.widgets.core import ColorInput
from wtforms.widgets.core import FileInput
from wtforms.widgets.core import HiddenInput
from wtforms.widgets.core import html_params
from wtforms.widgets.core import Input
from wtforms.widgets.core import ListWidget
from wtforms.widgets.core import NumberInput
from wtforms.widgets.core import PasswordInput
from wtforms.widgets.core import RadioInput
from wtforms.widgets.core import RangeInput
from wtforms.widgets.core import Select
from wtforms.widgets.core import TableWidget
from wtforms.widgets.core import TextArea
from wtforms.widgets.core import TextInput


def test_basic():
    assert html_params(foo=9, k="wuuu") == 'foo="9" k="wuuu"'
    assert html_params(class_="foo") == 'class="foo"'
    assert html_params(class__="foo") == 'class="foo"'
    assert html_params(for_="foo") == 'for="foo"'
    assert html_params(readonly=False, foo=9) == 'foo="9"'
    assert (
        html_params(accept="image/png, image/jpeg", required=True)
        == 'accept="image/png, image/jpeg" required'
    )


def test_data_prefix():
    assert html_params(data_foo=22) == 'data-foo="22"'
    assert html_params(data_foo_bar=1) == 'data-foo-bar="1"'


def test_aria_prefix():
    assert html_params(aria_foo="bar") == 'aria-foo="bar"'
    assert html_params(aria_foo_bar="foobar") == 'aria-foo-bar="foobar"'


def test_quoting():
    assert html_params(foo='hi&bye"quot') == 'foo="hi&amp;bye&#34;quot"'


def test_listwidget(dummy_field_class):
    # ListWidget just expects an iterable of field-like objects as its
    # 'field' so that is what we will give it
    field = dummy_field_class(
        [dummy_field_class(x, label="l" + x) for x in ["foo", "bar"]], id="hai"
    )

    assert ListWidget()(field) == '<ul id="hai"><li>lfoo foo</li><li>lbar bar</li></ul>'

    w = ListWidget(html_tag="ol", prefix_label=False)

    assert w(field) == '<ol id="hai"><li>foo lfoo</li><li>bar lbar</li></ol>'


def test_tablewidget(dummy_field_class):
    inner_fields = [
        dummy_field_class(data="hidden1", field_type="HiddenField"),
        dummy_field_class(data="foo", label="lfoo"),
        dummy_field_class(data="bar", label="lbar"),
        dummy_field_class(data="hidden2", field_type="HiddenField"),
    ]
    field = dummy_field_class(inner_fields, id="hai")
    assert (
        TableWidget(with_table_tag=True)(field)
        == '<table id="hai"><tr><th>lfoo</th><td>hidden1foo</td></tr>'
        "<tr><th>lbar</th><td>bar</td></tr></table>hidden2"
    )
    assert (
        TableWidget(with_table_tag=False)(field)
        == "<tr><th>lfoo</th><td>hidden1foo</td></tr>"
        "<tr><th>lbar</th><td>bar</td></tr>hidden2"
    )


def test_input_type():
    with pytest.raises(AttributeError):
        Input().input_type

    test_input = Input(input_type="test")
    assert test_input.input_type == "test"


def test_html_marking(basic_widget_dummy_field):
    html = TextInput()(basic_widget_dummy_field)
    assert hasattr(html, "__html__")
    assert html.__html__() is html


def test_text_input(basic_widget_dummy_field):
    assert (
        TextInput()(basic_widget_dummy_field)
        == '<input id="id" name="bar" type="text" value="foo">'
    )


def test_password_input(basic_widget_dummy_field):
    assert 'type="password"' in PasswordInput()(basic_widget_dummy_field)
    assert 'value=""' in PasswordInput()(basic_widget_dummy_field)
    assert 'value="foo"' in PasswordInput(hide_value=False)(basic_widget_dummy_field)


def test_hidden_input(basic_widget_dummy_field):
    assert 'type="hidden"' in HiddenInput()(basic_widget_dummy_field)
    assert "hidden" in HiddenInput().field_flags


def test_checkbox_input(basic_widget_dummy_field):
    assert (
        CheckboxInput()(basic_widget_dummy_field, value="v")
        == '<input checked id="id" name="bar" type="checkbox" value="v">'
    )
    # set falsy value to dummy field
    basic_widget_dummy_field.data = ""
    assert "checked" not in CheckboxInput()(basic_widget_dummy_field)
    basic_widget_dummy_field.data = False
    assert "checked" not in CheckboxInput()(basic_widget_dummy_field)


def test_radio_input(basic_widget_dummy_field):
    basic_widget_dummy_field.checked = True
    expected = '<input checked id="id" name="bar" type="radio" value="foo">'
    assert RadioInput()(basic_widget_dummy_field) == expected
    basic_widget_dummy_field.checked = False
    assert RadioInput()(basic_widget_dummy_field) == expected.replace(" checked", "")


def test_textarea(basic_widget_dummy_field):
    # Make sure textareas escape properly and render properly
    basic_widget_dummy_field.data = "hi<>bye"
    basic_widget_dummy_field.name = "f"
    basic_widget_dummy_field.id = ""
    assert (
        TextArea()(basic_widget_dummy_field)
        == '<textarea id="" name="f">\r\nhi&lt;&gt;bye</textarea>'
    )


def test_file(basic_widget_dummy_field):
    assert (
        FileInput()(basic_widget_dummy_field)
        == '<input id="id" name="bar" type="file">'
    )
    assert (
        FileInput(multiple=True)(basic_widget_dummy_field)
        == '<input id="id" multiple name="bar" type="file">'
    )


def test_color_input(basic_widget_dummy_field):
    assert 'type="color"' in ColorInput()(basic_widget_dummy_field)
    assert 'value="foo"' in ColorInput()(basic_widget_dummy_field)
    basic_widget_dummy_field.data = "#ff0000"
    assert 'value="#ff0000"' in ColorInput()(basic_widget_dummy_field)


def test_select(select_dummy_field):
    select_dummy_field.name = "f"

    assert (
        Select()(select_dummy_field)
        == '<select id="" name="f"><option selected value="foo">lfoo</option>'
        '<option value="bar">lbar</option></select>'
    )

    assert (
        Select(multiple=True)(select_dummy_field)
        == '<select id="" multiple name="f"><option selected value="foo">'
        'lfoo</option><option value="bar">lbar</option></select>'
    )


def test_render_option():
    # value, label, selected
    assert (
        Select.render_option("bar", "foo", False) == '<option value="bar">foo</option>'
    )

    assert (
        Select.render_option(True, "foo", True)
        == '<option selected value="True">foo</option>'
    )

    assert (
        Select.render_option("bar", '<i class="bar"></i>foo', False)
        == '<option value="bar">&lt;i class=&#34;bar&#34;&gt;&lt;/i&gt;foo</option>'
    )

    assert (
        Select.render_option("bar", Markup('<i class="bar"></i>foo'), False)
        == '<option value="bar"><i class="bar"></i>foo</option>'
    )


def test_number(html5_dummy_field):
    i1 = NumberInput(step="any")
    assert (
        i1(html5_dummy_field)
        == '<input id="id" name="bar" step="any" type="number" value="42">'
    )

    i2 = NumberInput(step=2)
    assert (
        i2(html5_dummy_field, step=3)
        == '<input id="id" name="bar" step="3" type="number" value="42">'
    )

    i3 = NumberInput(min=10)
    assert (
        i3(html5_dummy_field)
        == '<input id="id" min="10" name="bar" type="number" value="42">'
    )
    assert (
        i3(html5_dummy_field, min=5)
        == '<input id="id" min="5" name="bar" type="number" value="42">'
    )

    i4 = NumberInput(max=100)
    assert (
        i4(html5_dummy_field)
        == '<input id="id" max="100" name="bar" type="number" value="42">'
    )
    assert (
        i4(html5_dummy_field, max=50)
        == '<input id="id" max="50" name="bar" type="number" value="42">'
    )


def test_range(html5_dummy_field):
    i1 = RangeInput(step="any")
    assert (
        i1(html5_dummy_field)
        == '<input id="id" name="bar" step="any" type="range" value="42">'
    )

    i2 = RangeInput(step=2)
    assert (
        i2(html5_dummy_field, step=3)
        == '<input id="id" name="bar" step="3" type="range" value="42">'
    )
