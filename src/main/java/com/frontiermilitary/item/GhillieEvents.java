package com.frontiermilitary.item;

import com.frontiermilitary.FrontierMilitary;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Маскхалат: каждая надетая часть уменьшает дальность, с которой мобы замечают игрока; присед усиливает эффект. */
@Mod.EventBusSubscriber(modid = FrontierMilitary.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class GhillieEvents {
    @SubscribeEvent
    public static void onVisibility(LivingEvent.LivingVisibilityEvent event) {
        LivingEntity entity = event.getEntity();
        int pieces = 0;
        for (ItemStack stack : entity.getArmorSlots()) {
            if (stack.getItem() instanceof ArmorItem armor && armor.getMaterial() == ModArmorMaterials.GHILLIE) {
                pieces++;
            }
        }
        if (pieces > 0) {
            double factor = 1.0D - 0.15D * pieces;
            if (entity.isCrouching()) {
                factor *= 0.75D;
            }
            event.modifyVisibility(factor);
        }
    }

    private GhillieEvents() {}
}
