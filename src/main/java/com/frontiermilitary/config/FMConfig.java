package com.frontiermilitary.config;

import net.minecraftforge.common.ForgeConfigSpec;

public final class FMConfig {
    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.IntValue SMALL_CAMP_SPACING;
    public static final ForgeConfigSpec.IntValue LARGE_BASE_SPACING;
    public static final ForgeConfigSpec.DoubleValue PISTOL_DAMAGE;
    public static final ForgeConfigSpec.DoubleValue AK74_DAMAGE;
    public static final ForgeConfigSpec.DoubleValue SNIPER_DAMAGE;
    public static final ForgeConfigSpec.DoubleValue SHOTGUN_PELLET_DAMAGE;

    static {
        ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();
        builder.push("world_generation");
        SMALL_CAMP_SPACING = builder
                .comment("Reserved for future camp structure placement; lower values mean more frequent camps.")
                .defineInRange("smallCampSpacing", 24, 8, 128);
        LARGE_BASE_SPACING = builder
                .comment("Reserved for future base structure placement; higher values mean rarer bases.")
                .defineInRange("largeBaseSpacing", 96, 32, 512);
        builder.pop();
        builder.push("weapons");
        PISTOL_DAMAGE = builder
                .comment("Damage of one pistol bullet in half-hearts (headshots deal x1.5).")
                .defineInRange("pistolDamage", 7.0D, 1.0D, 50.0D);
        AK74_DAMAGE = builder
                .comment("Damage of one AK-74 bullet in half-hearts (headshots deal x1.5).")
                .defineInRange("ak74Damage", 6.0D, 1.0D, 50.0D);
        SNIPER_DAMAGE = builder
                .comment("Damage of one sniper rifle bullet in half-hearts (headshots deal x2.5).")
                .defineInRange("sniperDamage", 22.0D, 1.0D, 100.0D);
        SHOTGUN_PELLET_DAMAGE = builder
                .comment("Damage of ONE shotgun pellet in half-hearts (8 pellets per shot).")
                .defineInRange("shotgunPelletDamage", 3.0D, 0.5D, 30.0D);
        builder.pop();
        SPEC = builder.build();
    }

    private FMConfig() {}
}
