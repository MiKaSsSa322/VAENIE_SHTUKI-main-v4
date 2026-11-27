package com.frontiermilitary.client;

import com.frontiermilitary.FrontierMilitary;
import com.frontiermilitary.item.GunItem;
import com.frontiermilitary.item.MedkitItem;
import com.frontiermilitary.registry.ModEntities;
import com.frontiermilitary.registry.ModItems;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

import javax.annotation.Nullable;

/** Клиентская регистрация (MOD-шина): свойства моделей, рендерер пули, клавиша, HUD. */
@Mod.EventBusSubscriber(modid = FrontierMilitary.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientSetup {
    /** Тег-маркер «рисуем только руки» (ставится на временную копию стека в ClientForgeEvents). */
    public static final String TAG_FP_HANDS = "FpHands";

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            ResourceLocation state = new ResourceLocation(FrontierMilitary.MODID, "gun_state");
            ItemProperties.register(ModItems.PULSE_SIDEARM.get(), state, (stack, level, entity, seed) -> modelState(stack, level));
            ItemProperties.register(ModItems.AK74.get(), state, (stack, level, entity, seed) -> modelState(stack, level));
            ItemProperties.register(ModItems.SNIPER.get(), state, (stack, level, entity, seed) -> modelState(stack, level));
            ItemProperties.register(ModItems.SHOTGUN.get(), state, (stack, level, entity, seed) -> modelState(stack, level));
            ItemProperties.register(ModItems.MEDKIT.get(), new ResourceLocation(FrontierMilitary.MODID, "med_state"),
                    (stack, level, entity, seed) -> medState(stack, entity));
        });
    }

    /**
     * 0..8 — состояние самого оружия (state_N), 100..105 — только руки (hands_N).
     * Значения соответствуют predicate в models/item/<оружие>.json.
     */
    static float modelState(ItemStack stack, @Nullable ClientLevel level) {
        Level lv = level != null ? level : Minecraft.getInstance().level;
        if (lv == null || !(stack.getItem() instanceof GunItem gun)) {
            return 0.0F;
        }
        int state = gun.modelState(stack, lv.getGameTime());
        if (stack.hasTag() && stack.getTag().getBoolean(TAG_FP_HANDS)) {
            return 100 + gun.handIndex(state);
        }
        return state;
    }

    /** 100..106 — стадии перевязки (только для временной копии стека с TAG_FP_HANDS), иначе 0 — обычная иконка. */
    static float medState(ItemStack stack, @Nullable LivingEntity entity) {
        if (!(stack.hasTag() && stack.getTag().getBoolean(TAG_FP_HANDS))) {
            return 0.0F;
        }
        int stage = 0;
        if (entity != null && entity.isUsingItem()) {
            stage = Math.min(6, entity.getTicksUsingItem() * 7 / MedkitItem.USE_TICKS);
        }
        return 100 + stage;
    }

    @SubscribeEvent
    public static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.BULLET.get(), BulletRenderer::new);
    }

    @SubscribeEvent
    public static void onRegisterKeys(RegisterKeyMappingsEvent event) {
        event.register(ModKeys.RELOAD);
    }

    @SubscribeEvent
    public static void onRegisterOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAboveAll("scope", ScopeOverlay.OVERLAY);
        event.registerAboveAll("gun_ammo", GunHud.OVERLAY);
    }

    private ClientSetup() {}
}
