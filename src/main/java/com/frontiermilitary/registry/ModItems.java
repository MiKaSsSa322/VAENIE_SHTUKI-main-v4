package com.frontiermilitary.registry;

import com.frontiermilitary.FrontierMilitary;
import com.frontiermilitary.item.Ak74Item;
import com.frontiermilitary.item.MedkitItem;
import com.frontiermilitary.item.ShotgunItem;
import com.frontiermilitary.item.SniperRifleItem;
import com.frontiermilitary.item.ModArmorMaterials;
import com.frontiermilitary.item.ServicePistolItem;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, FrontierMilitary.MODID);

    /** Регистрационное имя pulse_sidearm сохранено ради совместимости с существующими мирами и ссылками. */
    public static final RegistryObject<Item> PULSE_SIDEARM = ITEMS.register("pulse_sidearm",
            () -> new ServicePistolItem(new Item.Properties().stacksTo(1).durability(256)));
    public static final RegistryObject<Item> PISTOL_AMMO = ITEMS.register("pistol_ammo",
            () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> AK74 = ITEMS.register("ak74",
            () -> new Ak74Item(new Item.Properties().stacksTo(1).durability(900)));
    public static final RegistryObject<Item> RIFLE_AMMO = ITEMS.register("rifle_ammo",
            () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> COMBAT_HELMET = ITEMS.register("combat_helmet",
            () -> new ArmorItem(ModArmorMaterials.COMBAT, ArmorItem.Type.HELMET, new Item.Properties()));
    public static final RegistryObject<Item> PLATE_CARRIER = ITEMS.register("plate_carrier",
            () -> new ArmorItem(ModArmorMaterials.COMBAT, ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final RegistryObject<Item> COMBAT_TROUSERS = ITEMS.register("combat_trousers",
            () -> new ArmorItem(ModArmorMaterials.COMBAT, ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final RegistryObject<Item> COMBAT_BOOTS = ITEMS.register("combat_boots",
            () -> new ArmorItem(ModArmorMaterials.COMBAT, ArmorItem.Type.BOOTS, new Item.Properties()));
    public static final RegistryObject<Item> SNIPER = ITEMS.register("sniper",
            () -> new SniperRifleItem(new Item.Properties().stacksTo(1).durability(600)));
    public static final RegistryObject<Item> SHOTGUN = ITEMS.register("shotgun",
            () -> new ShotgunItem(new Item.Properties().stacksTo(1).durability(500)));
    public static final RegistryObject<Item> SNIPER_AMMO = ITEMS.register("sniper_ammo", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> SHOTGUN_SHELLS = ITEMS.register("shotgun_shells", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> GHILLIE_HOOD = ITEMS.register("ghillie_hood",
            () -> new ArmorItem(ModArmorMaterials.GHILLIE, ArmorItem.Type.HELMET, new Item.Properties()));
    public static final RegistryObject<Item> GHILLIE_JACKET = ITEMS.register("ghillie_jacket",
            () -> new ArmorItem(ModArmorMaterials.GHILLIE, ArmorItem.Type.CHESTPLATE, new Item.Properties()));
    public static final RegistryObject<Item> GHILLIE_TROUSERS = ITEMS.register("ghillie_trousers",
            () -> new ArmorItem(ModArmorMaterials.GHILLIE, ArmorItem.Type.LEGGINGS, new Item.Properties()));
    public static final RegistryObject<Item> GHILLIE_WRAPS = ITEMS.register("ghillie_wraps",
            () -> new ArmorItem(ModArmorMaterials.GHILLIE, ArmorItem.Type.BOOTS, new Item.Properties()));
    public static final RegistryObject<Item> MEDKIT = ITEMS.register("medkit",
            () -> new MedkitItem(new Item.Properties().stacksTo(8)));
    public static final RegistryObject<Item> EMPTY_CANISTER = ITEMS.register("empty_canister",
            () -> new Item(new Item.Properties().stacksTo(1)));
    public static final RegistryObject<Item> FUEL_CANISTER = ITEMS.register("fuel_canister",
            () -> new Item(new Item.Properties().stacksTo(1)));
    public static final RegistryObject<Item> FIELD_RATION = ITEMS.register("field_ration",
            () -> new Item(new Item.Properties().food(
                    new net.minecraft.world.food.FoodProperties.Builder()
                            .nutrition(6).saturationMod(0.6F).build())));
    public static final RegistryObject<Item> REINFORCED_FIBER = ITEMS.register("reinforced_fiber",
            () -> new Item(new Item.Properties()));

    private ModItems() {}
}
