package com.frontiermilitary.item;

import com.frontiermilitary.registry.ModItems;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.function.Supplier;

/** Боевая экипировка: между железом и алмазом по защите, чинится усиленным волокном. */
public enum ModArmorMaterials implements ArmorMaterial {
    COMBAT("frontiermilitary:combat", 30, 3, 5, 7, 3, 12, SoundEvents.ARMOR_EQUIP_IRON, 1.0F, 0.0F,
            () -> Ingredient.of(ModItems.REINFORCED_FIBER.get())),
    GHILLIE("frontiermilitary:ghillie", 12, 1, 2, 3, 1, 15, SoundEvents.ARMOR_EQUIP_LEATHER, 0.0F, 0.0F,
            () -> Ingredient.of(ModItems.REINFORCED_FIBER.get()));

    private final String name;
    private final int durabilityMultiplier;
    private final int boots, leggings, chestplate, helmet;
    private final int enchantability;
    private final SoundEvent equipSound;
    private final float toughness;
    private final float knockbackResistance;
    private final Supplier<Ingredient> repair;

    ModArmorMaterials(String name, int durabilityMultiplier, int boots, int leggings, int chestplate, int helmet,
                      int enchantability, SoundEvent equipSound, float toughness, float knockbackResistance,
                      Supplier<Ingredient> repair) {
        this.name = name;
        this.durabilityMultiplier = durabilityMultiplier;
        this.boots = boots;
        this.leggings = leggings;
        this.chestplate = chestplate;
        this.helmet = helmet;
        this.enchantability = enchantability;
        this.equipSound = equipSound;
        this.toughness = toughness;
        this.knockbackResistance = knockbackResistance;
        this.repair = repair;
    }

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        switch (type) {
            case HELMET: return 11 * durabilityMultiplier;
            case CHESTPLATE: return 16 * durabilityMultiplier;
            case LEGGINGS: return 15 * durabilityMultiplier;
            default: return 13 * durabilityMultiplier;
        }
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        switch (type) {
            case HELMET: return helmet;
            case CHESTPLATE: return chestplate;
            case LEGGINGS: return leggings;
            default: return boots;
        }
    }

    @Override public int getEnchantmentValue() { return enchantability; }
    @Override public SoundEvent getEquipSound() { return equipSound; }
    @Override public Ingredient getRepairIngredient() { return repair.get(); }
    @Override public String getName() { return name; }
    @Override public float getToughness() { return toughness; }
    @Override public float getKnockbackResistance() { return knockbackResistance; }
}
