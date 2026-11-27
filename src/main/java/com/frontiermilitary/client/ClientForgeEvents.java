package com.frontiermilitary.client;

import com.frontiermilitary.FrontierMilitary;
import com.frontiermilitary.item.GunItem;
import com.frontiermilitary.item.MedkitItem;
import com.frontiermilitary.network.ModNetwork;
import com.frontiermilitary.network.ReloadPacket;
import com.frontiermilitary.network.TriggerPacket;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ComputeFovModifierEvent;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.client.event.MovementInputUpdateEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.event.RenderHandEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.AxisAngle4f;
import org.joml.Quaternionf;

/**
 * Клиентские события (FORGE-шина). Управление оружием: ЛКМ — выстрел, ПКМ — прицеливание, R — перезарядка.
 * Здесь же: плавный переход в позу прицеливания, зум FOV, отдача камеры, отрисовка рук с оружием/аптечкой.
 */
@Mod.EventBusSubscriber(modid = FrontierMilitary.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class ClientForgeEvents {
    private static boolean fireDown = false;
    private static boolean aimDown = false;
    private static long lastSeenShot = Long.MIN_VALUE;
    private static float aim = 0.0F;
    private static float prevAim = 0.0F;

    // ------------------------------------------------------------------ вспомогательное
    public static ItemStack heldGunStack(Player player) {
        if (player.getMainHandItem().getItem() instanceof GunItem) {
            return player.getMainHandItem();
        }
        if (player.getOffhandItem().getItem() instanceof GunItem) {
            return player.getOffhandItem();
        }
        return ItemStack.EMPTY;
    }

    /** Интерполированный прогресс прицеливания 0..1 со сглаживанием. */
    public static float aimProgress(float partialTick) {
        float t = Mth.lerp(partialTick, prevAim, aim);
        return t * t * (3.0F - 2.0F * t);
    }

    // ------------------------------------------------------------------ тик: курок, прицел, перезарядка, отдача
    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        ItemStack stack = player == null || mc.level == null ? ItemStack.EMPTY : heldGunStack(player);
        GunItem gun = stack.isEmpty() ? null : (GunItem) stack.getItem();
        long now = mc.level == null ? 0L : mc.level.getGameTime();

        while (ModKeys.RELOAD.consumeClick()) {
            if (gun != null && mc.screen == null) {
                ModNetwork.CHANNEL.sendToServer(new ReloadPacket());
            }
        }

        boolean canUse = gun != null && mc.screen == null;
        boolean wantFire = canUse && mc.options.keyAttack.isDown();
        boolean wantAim = canUse && mc.options.keyUse.isDown() && !player.isSprinting() && !gun.isReloading(stack, now);

        // плавный прогресс прицеливания
        prevAim = aim;
        if (gun != null) {
            float step = 1.0F / Math.max(1, gun.aimTicks());
            aim = Mth.clamp(aim + (wantAim ? step : -step * 1.5F), 0.0F, 1.0F);
        } else {
            aim = Mth.clamp(aim - 0.25F, 0.0F, 1.0F);
        }

        // на сервер отправляем только изменения состояния курка/прицела
        if (wantFire != fireDown || wantAim != aimDown) {
            fireDown = wantFire;
            aimDown = wantAim;
            ModNetwork.CHANNEL.sendToServer(new TriggerPacket(wantFire, wantAim));
        }

        // отдача в камеру: реагируем на новый выстрел, подтверждённый сервером
        if (gun != null) {
            CompoundTag tag = stack.getTag();
            if (tag != null && tag.contains(GunItem.TAG_LAST_SHOT)) {
                long shot = tag.getLong(GunItem.TAG_LAST_SHOT);
                if (shot != lastSeenShot) {
                    lastSeenShot = shot;
                    if (now - shot <= 3) {
                        float kick = gun.cameraKick() * (player.isShiftKeyDown() ? 0.7F : 1.0F) * (1.0F - 0.4F * aim);
                        player.setXRot(Math.max(-90.0F, player.getXRot() - kick));
                        player.setYRot(player.getYRot() + (player.getRandom().nextFloat() - 0.5F) * kick * 0.5F);
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------ ввод: ЛКМ/ПКМ принадлежат оружию
    @SubscribeEvent
    public static void onInteractionKey(InputEvent.InteractionKeyMappingTriggered event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && !heldGunStack(mc.player).isEmpty() && (event.isAttack() || event.isUseItem())) {
            event.setCanceled(true);
            event.setSwingHand(false);
        }
    }

    @SubscribeEvent
    public static void onFov(ComputeFovModifierEvent event) {
        Player player = event.getPlayer();
        ItemStack stack = heldGunStack(player);
        if (!stack.isEmpty() && aim > 0.0F) {
            float t = aimProgress(Minecraft.getInstance().getFrameTime());
            event.setNewFovModifier(event.getNewFovModifier() * Mth.lerp(t, 1.0F, ((GunItem) stack.getItem()).aimZoom()));
        }
    }

    @SubscribeEvent
    public static void onMovementInput(MovementInputUpdateEvent event) {
        if (aim > 0.0F) {
            float slow = 1.0F - 0.4F * aim;
            event.getInput().forwardImpulse *= slow;
            event.getInput().leftImpulse *= slow;
        }
    }

    @SubscribeEvent
    public static void onOverlayPre(RenderGuiOverlayEvent.Pre event) {
        Minecraft mc = Minecraft.getInstance();
        if (event.getOverlay() == VanillaGuiOverlay.CROSSHAIR.type() && mc.player != null
                && !heldGunStack(mc.player).isEmpty() && aim > 0.3F) {
            event.setCanceled(true); // при прицеливании ванильное перекрестие скрываем
        }
    }

    // ------------------------------------------------------------------ руки от первого лица
    @SubscribeEvent
    public static void onRenderHand(RenderHandEvent event) {
        ItemStack stack = event.getItemStack();
        if (stack.getItem() instanceof MedkitItem) {
            renderMedkit(event, stack);
            return;
        }
        if (!(stack.getItem() instanceof GunItem gun)) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || mc.level == null) {
            return;
        }
        boolean rightSide = (event.getHand() == InteractionHand.MAIN_HAND) == (player.getMainArm() == HumanoidArm.RIGHT);
        if (!rightSide) {
            return; // леворукий режим — стандартная отрисовка предмета
        }

        event.setCanceled(true);
        float pt = event.getPartialTick();
        float e = aimProgress(pt);
        if (gun.isScoped() && e > 0.85F) {
            return; // смотрим в оптику — модель оружия не рисуем (рисует ScopeOverlay)
        }

        PoseStack ps = event.getPoseStack();
        long now = mc.level.getGameTime();
        ps.pushPose();

        // поза прицеливания: сдвиг/поворот в пространстве камеры (рассчитано tools/tune_all.py)
        net.minecraft.resources.ResourceLocation key = ForgeRegistries.ITEMS.getKey(stack.getItem());
        float[] pose = key == null ? null : AimPoses.get(key.getPath());
        if (pose != null && e > 0.0F) {
            ps.translate(pose[0] * e, pose[1] * e, pose[2] * e);
            ps.mulPose(new Quaternionf(new AxisAngle4f((float) Math.toRadians(pose[3] * e), pose[4], pose[5], pose[6])));
        }

        ps.translate(0.56F, -0.52F + event.getEquipProgress() * -0.6F, -0.72F);
        applyAnimation(ps, gun, stack, now, pt, 1.0F - 0.5F * e);

        ItemRenderer renderer = mc.getItemRenderer();
        ItemStack hands = stack.copy();
        hands.getOrCreateTag().putBoolean(ClientSetup.TAG_FP_HANDS, true);
        renderer.renderStatic(player, hands, ItemDisplayContext.FIRST_PERSON_RIGHT_HAND, false, ps,
                event.getMultiBufferSource(), mc.level, event.getPackedLight(), OverlayTexture.NO_OVERLAY, 0);
        renderer.renderStatic(player, stack, ItemDisplayContext.FIRST_PERSON_RIGHT_HAND, false, ps,
                event.getMultiBufferSource(), mc.level, event.getPackedLight(), OverlayTexture.NO_OVERLAY, 0);
        ps.popPose();
    }

    /** Перевязка: пока идёт использование аптечки, рисуем руки с бинтом (стадии модели меняются по времени). */
    private static void renderMedkit(RenderHandEvent event, ItemStack stack) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || mc.level == null || !player.isUsingItem() || player.getUsedItemHand() != event.getHand()) {
            return;
        }
        if ((event.getHand() == InteractionHand.MAIN_HAND) != (player.getMainArm() == HumanoidArm.RIGHT)) {
            return;
        }
        event.setCanceled(true);
        PoseStack ps = event.getPoseStack();
        float t = player.getTicksUsingItem() + event.getPartialTick();
        ps.pushPose();
        ps.translate(0.56F, -0.52F + event.getEquipProgress() * -0.6F, -0.72F);
        ps.translate(0.0F, 0.006F * Mth.sin(t * 1.3F), 0.0F);
        ItemStack hands = stack.copy();
        hands.getOrCreateTag().putBoolean(ClientSetup.TAG_FP_HANDS, true);
        mc.getItemRenderer().renderStatic(player, hands, ItemDisplayContext.FIRST_PERSON_RIGHT_HAND, false, ps,
                event.getMultiBufferSource(), mc.level, event.getPackedLight(), OverlayTexture.NO_OVERLAY, 0);
        ps.popPose();
    }

    private static void applyAnimation(PoseStack ps, GunItem gun, ItemStack stack, long now, float pt, float strength) {
        // --- отдача: рывок на игрока и подброс ствола
        long since = gun.sinceShot(stack, now);
        if (since >= 0 && since < 12) {
            float t = since + pt;
            float k = Math.max(0.0F, 1.0F - t / (gun.isAutomatic() ? 4.0F : 8.0F));
            k = k * k * strength;
            ps.translate(0.0F, 0.012F * k, gun.recoilBack() * k);
            ps.mulPose(Axis.XP.rotationDegrees(gun.recoilPitch() * k));
        }

        // --- перезарядка: оружие чуть опускается и кренится, пока руки меняют магазин
        long reload = gun.reloadElapsed(stack, now);
        int total = gun.reloadTotal(stack);
        if (reload >= 0 && reload < total) {
            float p = Mth.clamp((reload + pt) / (float) total, 0.0F, 1.0F);
            float s = Math.min(1.0F, Mth.sin(p * (float) Math.PI) * 1.6F);
            ps.translate(-0.02F * s, -0.08F * s, 0.02F * s);
            ps.mulPose(Axis.XP.rotationDegrees(-9.0F * s));
            ps.mulPose(Axis.ZP.rotationDegrees(-13.0F * s));
            ps.mulPose(Axis.YP.rotationDegrees(7.0F * s));
        }
    }

    private ClientForgeEvents() {}
}
