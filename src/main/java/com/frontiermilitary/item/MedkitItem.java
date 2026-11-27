package com.frontiermilitary.item;

import com.frontiermilitary.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

import javax.annotation.Nullable;
import java.util.List;

/** Аптечка: удерживайте ПКМ ~2.4 с (перевязка), лечит 8 HP (4 сердца) — как «Мгновенное исцеление II». */
public class MedkitItem extends Item {
    public static final int USE_TICKS = 48;
    public static final float HEAL_AMOUNT = 8.0F;

    public MedkitItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getHealth() >= player.getMaxHealth()) {
            if (!level.isClientSide) {
                player.displayClientMessage(Component.translatable("message.frontiermilitary.health_full"), true);
            }
            return InteractionResultHolder.fail(stack);
        }
        player.startUsingItem(hand);
        if (!level.isClientSide) {
            level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.MEDKIT_RIP.get(),
                    SoundSource.PLAYERS, 0.8F, 1.0F);
        }
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void onUseTick(Level level, LivingEntity living, ItemStack stack, int remaining) {
        if (!level.isClientSide && remaining == USE_TICKS - 24) {
            level.playSound(null, living.getX(), living.getY(), living.getZ(), ModSounds.MEDKIT_RIP.get(),
                    SoundSource.PLAYERS, 0.6F, 0.85F);
        }
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity living) {
        if (!level.isClientSide) {
            living.heal(HEAL_AMOUNT);
            level.playSound(null, living.getX(), living.getY(), living.getZ(), ModSounds.MEDKIT_DONE.get(),
                    SoundSource.PLAYERS, 0.9F, 1.0F);
            if (level instanceof ServerLevel server) {
                server.sendParticles(ParticleTypes.HEART, living.getX(), living.getY() + 1.4D, living.getZ(),
                        5, 0.35D, 0.3D, 0.35D, 0.02D);
            }
        }
        if (living instanceof Player player) {
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
            player.getCooldowns().addCooldown(this, 20);
        }
        return stack;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return USE_TICKS;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.NONE;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.frontiermilitary.medkit").withStyle(ChatFormatting.GRAY));
    }
}
