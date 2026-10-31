-- 冒烟用例：被测模组生效 + 原生组件可用 + 延时任务能推进
local rabbit = TEST.Spawn("rabbit", 0, 0)
if rabbit == nil then
    TEST.Invalid("SpawnPrefab(rabbit) 返回 nil")
    return
end
TEST.Check("fixture tag applied", rabbit:HasTag("altwf_fixture"))
TEST.Equal("fixture server field", rabbit.altwf_fixture_value, 42)
TEST.Check("rabbit has health", rabbit.components.health ~= nil)
TEST.Metric("rabbit_max_health", rabbit.components.health and rabbit.components.health.maxhealth)
local t0 = GetTime()
TEST.After(1, function()
    TEST.Check("sim time advances", GetTime() - t0 >= 0.9, "dt=" .. tostring(GetTime() - t0))
    TEST.Done("smoke")
end)
