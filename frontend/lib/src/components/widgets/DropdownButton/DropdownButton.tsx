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

import React, { ReactElement, useState, useRef, useEffect } from "react"
import { useTheme } from "@emotion/react"
import { StatefulMenu } from "baseui/menu"
import { StatefulPopover, PLACEMENT } from "baseui/popover"
import { DropdownButton as DropdownButtonProto } from "@streamlit/protobuf"

import { WidgetStateManager } from "~lib/WidgetStateManager"
import { Box } from "~lib/components/shared/Base/styled-components"
import BaseButton, {
  BaseButtonKind,
  BaseButtonSize,
  BaseButtonTooltip,
  DynamicButtonLabel,
} from "~lib/components/shared/BaseButton"
import { EmotionTheme } from "~lib/theme"

export interface Props {
  disabled: boolean
  element: DropdownButtonProto
  widgetMgr: WidgetStateManager
  width?: number
}

export function DropdownButton({
  disabled,
  element,
  widgetMgr,
  width,
}: Props): ReactElement {
  const theme: EmotionTheme = useTheme()
  const [isOpen, setIsOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<string | null>(null)
  const prevSelectedItem = useRef<string | null>(null)

  useEffect(() => {
    // If the selected item changed, send the value to the widget manager
    if (selectedItem !== null && selectedItem !== prevSelectedItem.current) {
      widgetMgr.setStringValue(element.id, selectedItem)
      prevSelectedItem.current = selectedItem
    }
  }, [selectedItem, element.id, widgetMgr])

  // If the element has a value set from the backend, update the selected item
  useEffect(() => {
    if (element.setValue && element.selectedOption) {
      setSelectedItem(element.selectedOption)
      prevSelectedItem.current = element.selectedOption
    }
  }, [element.setValue, element.selectedOption])

  let kind = BaseButtonKind.SECONDARY
  if (element.type === "primary") {
    kind = BaseButtonKind.PRIMARY
  } else if (element.type === "tertiary") {
    kind = BaseButtonKind.TERTIARY
  }

  return (
    <Box className="stDropdownButton" data-testid="stDropdownButton">
      <BaseButtonTooltip help={element.help} containerWidth={element.useContainerWidth}>
        <StatefulPopover
          content={() => (
            <StatefulMenu
              items={element.options.map((option) => ({ label: option }))}
              onItemSelect={({ item }) => {
                setSelectedItem(item.label)
                setIsOpen(false)
              }}
            />
          )}
          isOpen={isOpen}
          onClickOutside={() => setIsOpen(false)}
          placement={PLACEMENT.bottomLeft}
          overrides={{
            Body: {
              style: {
                zIndex: theme.zIndices.popupZIndex,
              },
            },
          }}
        >
          <div>
            <BaseButton
              kind={kind}
              size={BaseButtonSize.SMALL}
              onClick={() => setIsOpen(!isOpen)}
              disabled={disabled}
              style={{ width: element.useContainerWidth ? "100%" : undefined }}
            >
              <DynamicButtonLabel icon={element.icon} label={element.label} />
            </BaseButton>
          </div>
        </StatefulPopover>
      </BaseButtonTooltip>
    </Box>
  )
}