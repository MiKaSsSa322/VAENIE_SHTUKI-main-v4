package com.frontiermilitary.registry;

import com.frontiermilitary.FrontierMilitary;
import com.frontiermilitary.block.FacingBlock;
import com.frontiermilitary.block.FloodlightBlock;
import com.frontiermilitary.block.FuelDrumBlock;
import com.frontiermilitary.block.GeneratorBlock;
import com.frontiermilitary.block.PowerCableBlock;
import net.minecraft.world.level.block.CarpetBlock;
import com.frontiermilitary.block.RazorWireBlock;
import com.frontiermilitary.block.ShapedBlock;
import net.minecraft.world.level.block.GlassBlock;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Supplier;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, FrontierMilitary.MODID);

    public static final RegistryObject<Block> METAL_FENCE = register("metal_fence",
            () -> new FenceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL)
                    .strength(5.0F, 6.0F).sound(SoundType.METAL).requiresCorrectToolForDrops()));
    public static final RegistryObject<Block> SECURITY_BARS = register("security_bars",
            () -> new IronBarsBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL)
                    .strength(5.0F, 6.0F).sound(SoundType.METAL).requiresCorrectToolForDrops()));
    public static final RegistryObject<Block> CONCRETE_BARRIER = register("concrete_barrier",
            () -> new WallBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GRAY)
                    .strength(8.0F, 12.0F).sound(SoundType.STONE).requiresCorrectToolForDrops()));
    public static final RegistryObject<Block> WATCH_POST_LAMP = register("watch_post_lamp",
            () -> new LanternBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL)
                    .strength(3.5F).sound(SoundType.LANTERN).lightLevel(state -> 15)
                    .noOcclusion().requiresCorrectToolForDrops()));

    // ---------------------------------------------------------------- новые блоки
    public static final RegistryObject<Block> SANDBAG_BLOCK = register("sandbag_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.SAND).strength(1.5F, 6.0F).sound(SoundType.SAND)));
    public static final RegistryObject<Block> SANDBAG_WALL = register("sandbag_wall",
            () -> new WallBlock(BlockBehaviour.Properties.of().mapColor(MapColor.SAND).strength(1.5F, 6.0F).sound(SoundType.SAND)));
    public static final RegistryObject<Block> HESCO_BARRIER = register("hesco_barrier",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.DIRT).strength(2.5F, 8.0F).sound(SoundType.GRAVEL)));
    public static final RegistryObject<Block> RAZOR_WIRE = register("razor_wire",
            () -> new RazorWireBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(1.0F)
                    .sound(SoundType.CHAIN).noCollission().noOcclusion()));
    public static final RegistryObject<Block> AMMO_CRATE = register("ammo_crate",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GREEN).strength(2.0F, 3.0F).sound(SoundType.WOOD)));
    public static final RegistryObject<Block> SUPPLY_CRATE = register("supply_crate",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2.0F, 3.0F).sound(SoundType.WOOD)));
    public static final RegistryObject<Block> FUEL_DRUM = register("fuel_drum",
            () -> new FuelDrumBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GREEN).strength(3.0F, 4.0F)
                    .sound(SoundType.METAL).noOcclusion()));
    public static final RegistryObject<Block> BUNKER_CONCRETE = register("bunker_concrete",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GRAY).strength(10.0F, 40.0F)
                    .sound(SoundType.STONE).requiresCorrectToolForDrops()));
    public static final RegistryObject<Block> STEEL_HULL_PLATE = register("steel_hull_plate",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(12.0F, 60.0F)
                    .sound(SoundType.METAL).requiresCorrectToolForDrops()));
    public static final RegistryObject<Block> CAMO_CONCRETE = register("camo_concrete",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GREEN).strength(6.0F, 20.0F)
                    .sound(SoundType.STONE).requiresCorrectToolForDrops()));
    public static final RegistryObject<Block> CAMO_NET = register("camo_net",
            () -> new CarpetBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GREEN).strength(0.3F)
                    .sound(SoundType.WOOL).noOcclusion()));
    public static final RegistryObject<Block> RADIO_STATION = register("radio_station",
            () -> new FacingBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GREEN).strength(3.5F)
                    .sound(SoundType.METAL).noOcclusion(), 2, 0, 3, 14, 16, 13));
    public static final RegistryObject<Block> FIELD_GENERATOR = register("field_generator",
            () -> new GeneratorBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GREEN).strength(4.0F)
                    .sound(SoundType.METAL).noOcclusion()));
    public static final RegistryObject<Block> FLOODLIGHT = register("floodlight",
            () -> new FloodlightBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(3.0F)
                    .sound(SoundType.METAL).lightLevel(state -> state.getValue(FloodlightBlock.LIT) ? 15 : 0).noOcclusion()));
    public static final RegistryObject<Block> TANK_TRAP = register("tank_trap",
            () -> new ShapedBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BROWN).strength(6.0F, 12.0F)
                    .sound(SoundType.METAL).noOcclusion().requiresCorrectToolForDrops(), 1, 0, 1, 15, 16, 15));
    public static final RegistryObject<Block> ARMORED_GLASS = register("armored_glass",
            () -> new GlassBlock(BlockBehaviour.Properties.of().mapColor(MapColor.NONE).strength(3.0F, 20.0F)
                    .sound(SoundType.GLASS).noOcclusion()));
    public static final RegistryObject<Block> MAP_TABLE = register("map_table",
            () -> new FacingBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2.0F)
                    .sound(SoundType.WOOD).noOcclusion(), 0, 0, 0, 16, 14, 16));
    public static final RegistryObject<Block> STEEL_GRATING = register("steel_grating",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(4.0F, 12.0F)
                    .sound(SoundType.METAL).noOcclusion()));
    public static final RegistryObject<Block> WARNING_SIGN = register("warning_sign",
            () -> new FacingBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_YELLOW).strength(1.5F)
                    .sound(SoundType.METAL).noOcclusion(), 3, 0, 7, 13, 16, 9));

    public static final RegistryObject<Block> POWER_CABLE = register("power_cable",
            () -> new PowerCableBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(0.2F)
                    .sound(SoundType.WOOL).noCollission().noOcclusion()));

    private static RegistryObject<Block> register(String name, Supplier<Block> block) {
        RegistryObject<Block> object = BLOCKS.register(name, block);
        ModItems.ITEMS.register(name, () -> new BlockItem(object.get(), new Item.Properties()));
        return object;
    }

    private ModBlocks() {}
}
