/**
 * Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React from "react"
import { screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { DropdownButton } from "./DropdownButton"
import { DropdownButton as DropdownButtonProto } from "@streamlit/protobuf"
import { render } from "~lib/test_util"
import { WidgetStateManager } from "~lib/WidgetStateManager"

const getProps = (elementProps: Partial<DropdownButtonProto> = {}): any => {
  const widgetMgr = new WidgetStateManager({
    sendRerunBackMsg: jest.fn(),
    formsDataChanged: jest.fn(),
  })
  const element = DropdownButtonProto.create({
    id: "1",
    label: "Open Menu",
    options: ["Item 1", "Item 2", "Item 3"],
    ...elementProps,
  })
  return {
    element,
    width: 300,
    disabled: false,
    widgetMgr,
  }
}

describe("DropdownButton widget", () => {
  it("renders without crashing", () => {
    render(<DropdownButton {...getProps()} />)
    expect(screen.getByText("Open Menu")).toBeInTheDocument()
  })

  it("shows menu when clicked", () => {
    render(<DropdownButton {...getProps()} />)
    fireEvent.click(screen.getByText("Open Menu"))
    expect(screen.getByText("Item 1")).toBeInTheDocument()
    expect(screen.getByText("Item 2")).toBeInTheDocument()
    expect(screen.getByText("Item 3")).toBeInTheDocument()
  })

  it("respects disabled prop", () => {
    render(<DropdownButton {...getProps()} disabled={true} />)
    const button = screen.getByText("Open Menu")
    expect(button).toBeDisabled()
  })

  it("displays the icon when provided", () => {
    render(<DropdownButton {...getProps({ icon: "🚨" })} />)
    expect(screen.getByText("🚨")).toBeInTheDocument()
  })

  it("sets the correct value when an item is selected", () => {
    const props = getProps()
    const spy = jest.spyOn(props.widgetMgr, "setStringValue")
    
    render(<DropdownButton {...props} />)
    fireEvent.click(screen.getByText("Open Menu"))
    fireEvent.click(screen.getByText("Item 2"))
    
    expect(spy).toHaveBeenCalledWith("1", "Item 2")
  })
})