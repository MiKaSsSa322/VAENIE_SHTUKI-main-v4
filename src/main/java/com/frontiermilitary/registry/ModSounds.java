package com.frontiermilitary.registry;

import com.frontiermilitary.FrontierMilitary;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, FrontierMilitary.MODID);

    public static final RegistryObject<SoundEvent> PISTOL_SHOT = reg("item.pistol.shot");
    public static final RegistryObject<SoundEvent> RIFLE_SHOT = reg("item.rifle.shot");
    public static final RegistryObject<SoundEvent> MEDKIT_RIP = reg("item.medkit.rip");
    public static final RegistryObject<SoundEvent> MEDKIT_DONE = reg("item.medkit.done");
    public static final RegistryObject<SoundEvent> GENERATOR_PULL = reg("block.generator.pull");
    public static final RegistryObject<SoundEvent> GENERATOR_START = reg("block.generator.start");
    public static final RegistryObject<SoundEvent> GENERATOR_RUN = reg("block.generator.run");
    public static final RegistryObject<SoundEvent> SNIPER_SHOT = reg("item.sniper.shot");
    public static final RegistryObject<SoundEvent> SHOTGUN_SHOT = reg("item.shotgun.shot");
    public static final RegistryObject<SoundEvent> SHOTGUN_PUMP = reg("item.shotgun.pump");
    public static final RegistryObject<SoundEvent> SHELL_IN = reg("item.shotgun.shell");
    public static final RegistryObject<SoundEvent> PISTOL_DRY = reg("item.pistol.dry");
    public static final RegistryObject<SoundEvent> MAG_OUT = reg("item.pistol.mag_out");
    public static final RegistryObject<SoundEvent> MAG_IN = reg("item.pistol.mag_in");
    public static final RegistryObject<SoundEvent> SLIDE_BACK = reg("item.pistol.slide_back");
    public static final RegistryObject<SoundEvent> SLIDE_FORWARD = reg("item.pistol.slide_forward");

    private static RegistryObject<SoundEvent> reg(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(
                new ResourceLocation(FrontierMilitary.MODID, name)));
    }

    private ModSounds() {}
}
