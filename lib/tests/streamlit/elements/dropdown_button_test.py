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

"""dropdown_button unit tests."""

from unittest.mock import MagicMock, patch

import pytest

import streamlit as st
from streamlit.errors import StreamlitAPIException
from streamlit.proto.DropdownButton_pb2 import DropdownButton
from tests.delta_generator_test_case import DeltaGeneratorTestCase


class DropdownButtonTest(DeltaGeneratorTestCase):
    """Test dropdown_button functionality."""

    def test_dropdown_button_required_fields(self):
        """Test that dropdown_button requires label and options."""
        st.dropdown_button("Open Menu", options=["Item 1", "Item 2"])

        c = self.get_delta_from_queue().new_element.dropdown_button
        self.assertEqual(c.label, "Open Menu")
        self.assertEqual(c.options, ["Item 1", "Item 2"])

    def test_dropdown_button_just_label(self):
        """Test that dropdown_button requires options."""
        with pytest.raises(TypeError):
            st.dropdown_button("Open Menu")

    def test_dropdown_button_optional_fields(self):
        """Test dropdown_button's optional params."""
        st.dropdown_button(
            label="Open Menu",
            options=["Item 1", "Item 2"],
            key="dropdown",
            help="Open a menu",
            type="primary",
            icon="🚨",
            disabled=True,
            use_container_width=True,
        )

        c = self.get_delta_from_queue().new_element.dropdown_button
        self.assertEqual(c.label, "Open Menu")
        self.assertEqual(c.options, ["Item 1", "Item 2"])
        self.assertEqual(c.help, "Open a menu")
        self.assertEqual(c.type, "primary")
        self.assertEqual(c.icon, "🚨")
        self.assertEqual(c.disabled, True)
        self.assertEqual(c.use_container_width, True)

    def test_dropdown_button_invalid_type(self):
        """Test that invalid button type raises an exception."""
        with pytest.raises(StreamlitAPIException):
            st.dropdown_button("Open Menu", options=["Item 1"], type="invalid")

    def test_dropdown_button_in_form(self):
        """Test that dropdown_button raises an exception when used in a form."""
        with self.assertRaises(StreamlitAPIException) as ctx:
            with st.form("form"):
                st.dropdown_button("Open Menu", options=["Item 1"])
        self.assertTrue("can't be used in" in str(ctx.exception))