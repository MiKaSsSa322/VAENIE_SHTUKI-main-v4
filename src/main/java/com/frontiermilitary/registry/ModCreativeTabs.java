package com.frontiermilitary.registry;

import com.frontiermilitary.FrontierMilitary;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModCreativeTabs {

    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(
                    Registries.CREATIVE_MODE_TAB,
                    FrontierMilitary.MODID
            );

    public static final RegistryObject<CreativeModeTab> MAIN =
            TABS.register("main",
                    () -> CreativeModeTab.builder()
                            .title(Component.translatable("itemGroup.frontiermilitary"))
                            .icon(() -> ModItems.PULSE_SIDEARM.get().getDefaultInstance())
                            .displayItems((parameters, output) -> {
                                output.accept(ModItems.PULSE_SIDEARM.get().getDefaultInstance());
                                output.accept(ModItems.PISTOL_AMMO.get());
                                output.accept(ModItems.AK74.get().getDefaultInstance());
                                output.accept(ModItems.SNIPER.get().getDefaultInstance());
                                output.accept(ModItems.SHOTGUN.get().getDefaultInstance());
                                output.accept(ModItems.SNIPER_AMMO.get());
                                output.accept(ModItems.SHOTGUN_SHELLS.get());
                                output.accept(ModItems.RIFLE_AMMO.get());
                                output.accept(ModItems.COMBAT_HELMET.get());
                                output.accept(ModItems.PLATE_CARRIER.get());
                                output.accept(ModItems.COMBAT_TROUSERS.get());
                                output.accept(ModItems.COMBAT_BOOTS.get());
                                output.accept(ModItems.GHILLIE_HOOD.get());
                                output.accept(ModItems.GHILLIE_JACKET.get());
                                output.accept(ModItems.GHILLIE_TROUSERS.get());
                                output.accept(ModItems.GHILLIE_WRAPS.get());
                                output.accept(ModItems.FIELD_RATION.get());
                                output.accept(ModItems.MEDKIT.get());
                                output.accept(ModItems.EMPTY_CANISTER.get());
                                output.accept(ModItems.FUEL_CANISTER.get());
                                output.accept(ModItems.REINFORCED_FIBER.get());

                                output.accept(ModBlocks.SANDBAG_BLOCK.get());
                                output.accept(ModBlocks.SANDBAG_WALL.get());
                                output.accept(ModBlocks.HESCO_BARRIER.get());
                                output.accept(ModBlocks.CONCRETE_BARRIER.get());
                                output.accept(ModBlocks.BUNKER_CONCRETE.get());
                                output.accept(ModBlocks.STEEL_HULL_PLATE.get());
                                output.accept(ModBlocks.CAMO_CONCRETE.get());
                                output.accept(ModBlocks.ARMORED_GLASS.get());
                                output.accept(ModBlocks.STEEL_GRATING.get());
                                output.accept(ModBlocks.METAL_FENCE.get());
                                output.accept(ModBlocks.SECURITY_BARS.get());
                                output.accept(ModBlocks.RAZOR_WIRE.get());
                                output.accept(ModBlocks.TANK_TRAP.get());
                                output.accept(ModBlocks.CAMO_NET.get());
                                output.accept(ModBlocks.AMMO_CRATE.get());
                                output.accept(ModBlocks.SUPPLY_CRATE.get());
                                output.accept(ModBlocks.FUEL_DRUM.get());
                                output.accept(ModBlocks.RADIO_STATION.get());
                                output.accept(ModBlocks.FIELD_GENERATOR.get());
                                output.accept(ModBlocks.FLOODLIGHT.get());
                                output.accept(ModBlocks.POWER_CABLE.get());
                                output.accept(ModBlocks.WATCH_POST_LAMP.get());
                                output.accept(ModBlocks.MAP_TABLE.get());
                                output.accept(ModBlocks.WARNING_SIGN.get());
                            })
                            .build()
            );

    private ModCreativeTabs() {}
}
