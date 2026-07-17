local Widget = require('widgets/widget')
local Text = require('widgets/text')

local ModWidget = Class(Widget, function(self)
    Widget._ctor(self, 'ModWidget')

    self.label = self:AddChild(Text(BODYTEXTFONT, 24, ''))
    self.label:SetPosition(0, 0)
    self:SetValue('')
end)

function ModWidget:SetValue(value)
    self.label:SetString(tostring(value or ''))
end

function ModWidget:OnControl(control, down)
    if ModWidget._base.OnControl(self, control, down) then
        return true
    end

    return false
end

function ModWidget:Kill()
    -- Remove external event and input callbacks before the base Kill.
    ModWidget._base.Kill(self)
end

return ModWidget
