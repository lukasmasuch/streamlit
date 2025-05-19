# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Literal, cast

from streamlit.dataframe_util import OptionSequence, convert_anything_to_list
from streamlit.elements.lib.form_utils import current_form_id, is_in_form
from streamlit.elements.lib.policies import check_widget_policies
from streamlit.elements.lib.utils import (
    Key,
    compute_and_register_element_id,
    save_for_app_testing,
    to_key,
)
from streamlit.errors import StreamlitAPIException
from streamlit.proto.DropdownButton_pb2 import DropdownButton as DropdownButtonProto
from streamlit.runtime.metrics_util import gather_metrics
from streamlit.runtime.scriptrunner import ScriptRunContext, get_script_run_ctx
from streamlit.runtime.state import (
    WidgetArgs,
    WidgetCallback,
    WidgetKwargs,
    register_widget,
)
from streamlit.string_util import validate_icon_or_emoji
from streamlit.type_util import check_python_comparable

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator

FORM_DOCS_INFO = """

For more information, refer to the
[documentation for forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form).
"""


@dataclass
class DropdownButtonSerde:
    def serialize(self, v: str | None) -> str:
        return v or ""

    def deserialize(self, ui_value: str | None) -> str | None:
        return ui_value


class DropdownButtonMixin:
    @gather_metrics("dropdown_button")
    def dropdown_button(
        self,
        label: str,
        options: OptionSequence[Any],
        key: Key | None = None,
        help: str | None = None,
        on_click: WidgetCallback | None = None,
        args: WidgetArgs | None = None,
        kwargs: WidgetKwargs | None = None,
        *,  # keyword-only arguments:
        type: Literal["primary", "secondary", "tertiary"] = "secondary",
        icon: str | None = None,
        disabled: bool = False,
        use_container_width: bool = False,
    ) -> str | None:
        r"""Display a dropdown button widget.

        Parameters
        ----------
        label : str
            A short label explaining to the user what this button is for.
            The label can optionally contain GitHub-flavored Markdown of the
            following types: Bold, Italics, Strikethroughs, Inline Code, Links,
            and Images. Images display like icons, with a max height equal to
            the font height.

            Unsupported Markdown elements are unwrapped so only their children
            (text contents) render. Display unsupported elements as literal
            characters by backslash-escaping them. E.g.,
            ``"1\. Not an ordered list"``.

        options : sequence
            A sequence of options for the dropdown menu. The labels in the menu
            will be rendered as strings.

        key : str or int
            An optional string or integer to use as the unique key for the widget.
            If this is omitted, a key will be generated for the widget
            based on its content. No two widgets may have the same key.

        help : str or None
            A tooltip that gets displayed when the button is hovered over. If
            this is ``None`` (default), no tooltip is displayed.

            The tooltip can optionally contain GitHub-flavored Markdown,
            including the Markdown directives described in the ``body``
            parameter of ``st.markdown``.

        on_click : callable
            An optional callback invoked when this button is clicked.

        args : tuple
            An optional tuple of args to pass to the callback.

        kwargs : dict
            An optional dict of kwargs to pass to the callback.

        type : "primary", "secondary", or "tertiary"
            An optional string that specifies the button type. This can be one
            of the following:

            - ``"primary"``: The button's background is the app's primary color
              for additional emphasis.
            - ``"secondary"`` (default): The button's background coordinates
              with the app's background color for normal emphasis.
            - ``"tertiary"``: The button is plain text without a border or
              background for subtly.

        icon : str or None
            An optional emoji or icon to display next to the button label. If ``icon``
            is ``None`` (default), no icon is displayed. If ``icon`` is a
            string, the following options are valid:

            - A single-character emoji. For example, you can set ``icon="🚨"``
              or ``icon="🔥"``. Emoji short codes are not supported.

            - An icon from the Material Symbols library (rounded style) in the
              format ``":material/icon_name:"`` where "icon_name" is the name
              of the icon in snake case.

              For example, ``icon=":material/thumb_up:"`` will display the
              Thumb Up icon. Find additional icons in the `Material Symbols \
              <https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded>`_
              font library.

        disabled : bool
            An optional boolean that disables the button if set to ``True``.
            The default is ``False``.

        use_container_width : bool
            Whether to expand the button's width to fill its parent container.
            If ``use_container_width`` is ``False`` (default), Streamlit sizes
            the button to fit its contents. If ``use_container_width`` is
            ``True``, the width of the button matches its parent container.

            In both cases, if the contents of the button are wider than the
            parent container, the contents will line wrap.

        Returns
        -------
        str or None
            The selected option when clicked, or None if nothing is selected.

        Examples
        --------
        >>> import streamlit as st
        >>>
        >>> action = st.dropdown_button("Open Menu", options=["Item One", "Item Two", "Item Three"])
        >>> if action == "Item One":
        >>>     st.write("You selected Item One")
        >>> elif action == "Item Two":
        >>>     st.write("You selected Item Two")
        >>> elif action == "Item Three":
        >>>     st.write("You selected Item Three")

        """
        key = to_key(key)
        ctx = get_script_run_ctx()

        # Checks whether the entered button type is one of the allowed options
        if type not in ["primary", "secondary", "tertiary"]:
            raise StreamlitAPIException(
                'The type argument to st.dropdown_button must be "primary", "secondary", or "tertiary". '
                f'\nThe argument passed was "{type}".'
            )

        # Convert the options to a list and check if they can be compared
        opt = convert_anything_to_list(options)
        check_python_comparable(opt)

        check_widget_policies(
            self.dg,
            key,
            on_click,
            default_value=None,
            writes_allowed=False,
        )

        # Compute a unique ID for the dropdown button
        element_id = compute_and_register_element_id(
            "dropdown_button",
            user_key=key,
            form_id=current_form_id(self.dg),
            label=label,
            options=[str(option) for option in opt],
            icon=icon,
            help=help,
            type=type,
            use_container_width=use_container_width,
        )

        # Check if we are in a form (not allowed)
        if is_in_form(self.dg):
            raise StreamlitAPIException(
                f"`st.dropdown_button()` can't be used in an `st.form()`.{FORM_DOCS_INFO}"
            )

        # Create the proto message for the dropdown button
        dropdown_button_proto = DropdownButtonProto()
        dropdown_button_proto.id = element_id
        dropdown_button_proto.label = label
        dropdown_button_proto.use_container_width = use_container_width
        dropdown_button_proto.options.extend([str(option) for option in opt])
        dropdown_button_proto.type = type
        dropdown_button_proto.disabled = disabled
        dropdown_button_proto.set_value = False

        if help is not None:
            dropdown_button_proto.help = dedent(help)

        if icon is not None:
            dropdown_button_proto.icon = validate_icon_or_emoji(icon)

        # Register the widget in the state system
        serde = DropdownButtonSerde()
        button_state = register_widget(
            dropdown_button_proto.id,
            on_change_handler=on_click,
            args=args,
            kwargs=kwargs,
            deserializer=serde.deserialize,
            serializer=serde.serialize,
            ctx=ctx,
            value_type="string_value",
        )

        # If the state changed (button was clicked), update the proto
        if button_state.value_changed:
            dropdown_button_proto.selected_option = serde.serialize(button_state.value)
            dropdown_button_proto.set_value = True

        # Save for app testing and send the proto to the frontend
        if ctx:
            save_for_app_testing(ctx, element_id, button_state.value)
        self.dg._enqueue("dropdown_button", dropdown_button_proto)

        return button_state.value

    @property
    def dg(self) -> DeltaGenerator:
        """Get our DeltaGenerator."""
        return cast("DeltaGenerator", self)