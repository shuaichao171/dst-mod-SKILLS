-- 给兔子加一个标签和一个字段，行为脚本据此确认被测模组确实加载并生效
AddPrefabPostInit("rabbit", function(inst)
    inst:AddTag("altwf_fixture")
    if GLOBAL.TheWorld.ismastersim then
        inst.altwf_fixture_value = 42
    end
end)
