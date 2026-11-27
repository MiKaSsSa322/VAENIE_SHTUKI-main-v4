package com.frontiermilitary.item;

import com.frontiermilitary.entity.BulletEntity;
import com.frontiermilitary.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;

import javax.annotation.Nullable;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * Общая логика огнестрельного оружия. Состояние (патроны, перезарядка, курок, прицел) хранится в NBT предмета.
 * Управление: ЛКМ — выстрел, ПКМ — прицеливание, R — перезарядка. Клиент шлёт состояние курка/прицела пакетом.
 */
public abstract class GunItem extends Item {
    public static final String TAG_AMMO = "Ammo";
    public static final String TAG_LAST_SHOT = "LastShot";
    public static final String TAG_RELOAD_START = "ReloadStart";
    public static final String TAG_RELOAD_TOTAL = "ReloadTotal";
    public static final String TAG_TRIGGER = "Trigger";
    public static final String TAG_AIM = "Aim";

    private final int magSize;
    private final int reloadTicks;
    private final int cooldown;
    private final boolean automatic;
    private final float bulletSpeed;
    private final float inaccuracy;
    private final float inaccuracySneak;
    private final float inaccuracySprint;
    private final Supplier<? extends Item> ammoItem;
    private final Supplier<Double> damage;
    private final Supplier<SoundEvent> shotSound;

    // настраиваются в конструкторах наследников
    protected int pellets = 1;
    protected boolean perShell = false;
    protected int shellSetup = 6;
    protected int shellTicks = 12;
    protected int bulletLife = 30;
    protected double bulletGravity = 0.004D;
    protected float headshot = 1.5F;
    protected float aimSpreadFactor = 0.25F;
    protected float aimZoom = 0.9F;
    protected boolean scoped = false;
    protected int aimTicks = 5;

    protected GunItem(Properties properties, int magSize, int reloadTicks, int cooldown, boolean automatic,
                      float bulletSpeed, float inaccuracy, float inaccuracySneak, float inaccuracySprint,
                      Supplier<? extends Item> ammoItem, Supplier<Double> damage, Supplier<SoundEvent> shotSound) {
        super(properties);
        this.magSize = magSize;
        this.reloadTicks = reloadTicks;
        this.cooldown = cooldown;
        this.automatic = automatic;
        this.bulletSpeed = bulletSpeed;
        this.inaccuracy = inaccuracy;
        this.inaccuracySneak = inaccuracySneak;
        this.inaccuracySprint = inaccuracySprint;
        this.ammoItem = ammoItem;
        this.damage = damage;
        this.shotSound = shotSound;
    }

    // ------------------------------------------------------------------ параметры для клиента
    public int magSize() { return magSize; }
    public boolean isAutomatic() { return automatic; }
    public float aimZoom() { return aimZoom; }
    public boolean isScoped() { return scoped; }
    public int aimTicks() { return aimTicks; }

    /** Полная длительность текущей перезарядки (для дробовика зависит от числа вставляемых патронов). */
    public int reloadTotal(ItemStack stack) {
        if (perShell) {
            CompoundTag tag = stack.getTag();
            if (tag != null && tag.contains(TAG_RELOAD_TOTAL)) {
                return tag.getInt(TAG_RELOAD_TOTAL);
            }
            return shellSetup + shellTicks * magSize;
        }
        return reloadTicks;
    }

    /** Номер состояния 3D-модели (state_N.json). */
    public abstract int modelState(ItemStack stack, long now);

    public int handIndex(int state) {
        switch (state) {
            case 4: return 1;
            case 5: return 2;
            case 6: return 3;
            case 7: return 4;
            case 8: return 5;
            default: return 0;
        }
    }

    protected abstract void reloadSounds(Level level, Entity holder, long elapsed);
    /** Звуки после выстрела (цикл затвора/помпы); since — тиков с выстрела. */
    protected void postShot(Level level, Entity holder, long since) {}

    public abstract float recoilBack();
    public abstract float recoilPitch();
    public abstract float cameraKick();

    // ------------------------------------------------------------------ состояние в NBT
    /** Предмет без тега (выданный командой) считается заряженным. */
    public int getAmmo(ItemStack stack) {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(TAG_AMMO)) {
            return magSize;
        }
        return Math.max(0, Math.min(magSize, tag.getInt(TAG_AMMO)));
    }

    public void setAmmo(ItemStack stack, int ammo) {
        stack.getOrCreateTag().putInt(TAG_AMMO, Math.max(0, Math.min(magSize, ammo)));
    }

    public boolean isReloading(ItemStack stack, long now) {
        long e = reloadElapsed(stack, now);
        return e >= 0 && e < reloadTotal(stack);
    }

    public long reloadElapsed(ItemStack stack, long now) {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(TAG_RELOAD_START)) {
            return -1;
        }
        return Math.max(0, now - tag.getLong(TAG_RELOAD_START));
    }

    public long sinceShot(ItemStack stack, long now) {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(TAG_LAST_SHOT)) {
            return -1;
        }
        return Math.max(0, now - tag.getLong(TAG_LAST_SHOT));
    }

    @Override
    public ItemStack getDefaultInstance() {
        ItemStack stack = super.getDefaultInstance();
        setAmmo(stack, magSize);
        return stack;
    }

    // ------------------------------------------------------------------ управление
    /** ПКМ оружием ничего не делает (прицеливание обрабатывает клиент), чтобы не открывались ящики и т. п. */
    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        return InteractionResultHolder.pass(player.getItemInHand(hand));
    }

    /** С оружием в руках нельзя ломать блоки (ЛКМ — выстрел). */
    @Override
    public boolean canAttackBlock(BlockState state, Level level, BlockPos pos, Player player) {
        return false;
    }

    /** Обработка пакета курка: pressed — ЛКМ зажата, aiming — ПКМ зажата. */
    public void onTrigger(ServerPlayer player, ItemStack stack, InteractionHand hand, boolean pressed, boolean aiming) {
        CompoundTag tag = stack.getOrCreateTag();
        if (aiming) {
            tag.putBoolean(TAG_AIM, true);
        } else {
            tag.remove(TAG_AIM);
        }
        if (automatic) {
            if (pressed) {
                tag.putBoolean(TAG_TRIGGER, true);
            } else {
                tag.remove(TAG_TRIGGER);
            }
            return;
        }
        if (!pressed) {
            return;
        }
        Level level = player.level();
        long now = level.getGameTime();
        if (isReloading(stack, now)) {
            if (perShell && getAmmo(stack) > 0) {
                tag.remove(TAG_RELOAD_START); // дробовик: выстрел прерывает дозарядку
            } else {
                return;
            }
        }
        if (getAmmo(stack) <= 0) {
            onEmptyTrigger(player, stack, level);
            return;
        }
        long since = sinceShot(stack, now);
        if (since < 0 || since >= cooldown) {
            serverFire((ServerLevel) level, player, stack, hand, now);
        }
    }

    /** Один выстрел (только сервер). */
    protected void serverFire(ServerLevel level, Player player, ItemStack stack, InteractionHand hand, long now) {
        setAmmo(stack, getAmmo(stack) - 1);
        CompoundTag tag = stack.getOrCreateTag();
        tag.putLong(TAG_LAST_SHOT, now);

        Vec3 look = player.getLookAngle();
        boolean aiming = tag.getBoolean(TAG_AIM);
        float spread = player.isSprinting() ? inaccuracySprint : (player.isShiftKeyDown() ? inaccuracySneak : inaccuracy);
        if (aiming) {
            spread *= aimSpreadFactor;
        }

        for (int i = 0; i < pellets; i++) {
            BulletEntity bullet = new BulletEntity(level, player, damage.get().floatValue());
            bullet.setMaxLife(bulletLife);
            bullet.setGravity(bulletGravity);
            bullet.setHeadshot(headshot);
            bullet.setPos(player.getEyePosition().add(look.scale(0.6D)).add(0.0D, -0.1D, 0.0D));
            bullet.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, bulletSpeed, spread);
            level.addFreshEntity(bullet);
        }

        // эффекты у дульного среза: смещён вправо-вперёд от глаз (при прицеливании — по центру)
        Vec3 right = look.cross(new Vec3(0.0D, 1.0D, 0.0D)).normalize();
        boolean rightHand = (hand == InteractionHand.MAIN_HAND) == (player.getMainArm() == HumanoidArm.RIGHT);
        double side = aiming ? 0.0D : (rightHand ? 1.0D : -1.0D);
        Vec3 muzzle = player.getEyePosition().add(look.scale(1.1D)).add(right.scale(0.16D * side)).add(0.0D, aiming ? -0.05D : -0.14D, 0.0D);
        level.sendParticles(ParticleTypes.FLAME, muzzle.x, muzzle.y, muzzle.z, 2, 0.01D, 0.01D, 0.01D, 0.01D);
        level.sendParticles(ParticleTypes.SMOKE, muzzle.x, muzzle.y, muzzle.z, 3, 0.03D, 0.03D, 0.03D, 0.012D);
        playAt(level, player, shotSound.get(), 1.0F, 0.95F + level.random.nextFloat() * 0.1F);

        stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
    }

    /** Курок нажат при пустом магазине: автоперезарядка или сухой щелчок. */
    protected void onEmptyTrigger(Player player, ItemStack stack, Level level) {
        if (hasReserve(player)) {
            startReload(player, stack, level);
        } else {
            player.displayClientMessage(Component.translatable("message.frontiermilitary.no_ammo"), true);
            playAt(level, player, ModSounds.PISTOL_DRY.get(), 0.8F, 1.0F);
        }
    }

    // ------------------------------------------------------------------ перезарядка
    /** Запускает перезарядку (только сервер). */
    public static boolean startReload(Player player, ItemStack stack, Level level) {
        if (level.isClientSide || !(stack.getItem() instanceof GunItem gun)) {
            return false;
        }
        long now = level.getGameTime();
        if (gun.isReloading(stack, now) || gun.getAmmo(stack) >= gun.magSize) {
            return false;
        }
        if (!gun.hasReserve(player)) {
            player.displayClientMessage(Component.translatable("message.frontiermilitary.no_ammo"), true);
            return false;
        }
        CompoundTag tag = stack.getOrCreateTag();
        tag.putLong(TAG_RELOAD_START, now);
        tag.remove(TAG_TRIGGER);
        if (gun.perShell) {
            int missing = gun.magSize - gun.getAmmo(stack);
            if (!player.getAbilities().instabuild) {
                missing = Math.min(missing, gun.countAmmo(player));
            }
            tag.putInt(TAG_RELOAD_TOTAL, gun.shellSetup + gun.shellTicks * missing);
        }
        return true;
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        if (level.isClientSide || !(entity instanceof LivingEntity living)) {
            return;
        }
        CompoundTag tag = stack.getTag();
        if (tag == null) {
            return;
        }
        InteractionHand hand = living.getMainHandItem() == stack ? InteractionHand.MAIN_HAND
                : (living.getOffhandItem() == stack ? InteractionHand.OFF_HAND : null);
        long now = level.getGameTime();

        if (hand == null) {
            tag.remove(TAG_AIM); // оружие не в руках — сбрасываем прицел и курок
            tag.remove(TAG_TRIGGER);
        } else {
            long sinceNow = sinceShot(stack, now);
            if (sinceNow >= 0 && sinceNow < 40) {
                postShot(level, entity, sinceNow);
            }
        }

        // --- автоматический огонь
        if (automatic && tag.getBoolean(TAG_TRIGGER)) {
            if (hand == null || !(entity instanceof Player player)) {
                tag.remove(TAG_TRIGGER);
            } else if (!isReloading(stack, now)) {
                if (getAmmo(stack) <= 0) {
                    onEmptyTrigger(player, stack, level);
                    tag.remove(TAG_TRIGGER);
                } else {
                    long since = sinceShot(stack, now);
                    if (since < 0 || since >= cooldown) {
                        serverFire((ServerLevel) level, player, stack, hand, now);
                    }
                }
            }
        }

        // --- перезарядка
        if (!tag.contains(TAG_RELOAD_START)) {
            return;
        }
        long elapsed = now - tag.getLong(TAG_RELOAD_START);
        if (hand == null || elapsed < 0) {
            tag.remove(TAG_RELOAD_START); // оружие убрали из рук — перезарядка отменена
            return;
        }
        int total = reloadTotal(stack);

        if (perShell) {
            if (elapsed >= shellSetup && (elapsed - shellSetup) % shellTicks == shellTicks - 1
                    && entity instanceof Player player && getAmmo(stack) < magSize) {
                int taken = player.getAbilities().instabuild ? 1 : consumeAmmo(player, 1);
                if (taken > 0) {
                    setAmmo(stack, getAmmo(stack) + 1);
                    playAt(level, entity, ModSounds.SHELL_IN.get(), 0.8F, 1.0F);
                } else {
                    tag.remove(TAG_RELOAD_START);
                    return;
                }
            }
            if (elapsed >= total) {
                tag.remove(TAG_RELOAD_START);
                tag.remove(TAG_RELOAD_TOTAL);
            }
            return;
        }

        reloadSounds(level, entity, elapsed);
        if (elapsed >= total) {
            if (entity instanceof Player player) {
                int need = magSize - getAmmo(stack);
                int taken = player.getAbilities().instabuild ? need : consumeAmmo(player, need);
                setAmmo(stack, getAmmo(stack) + taken);
            }
            tag.remove(TAG_RELOAD_START);
        }
    }

    public boolean hasReserve(Player player) {
        return player.getAbilities().instabuild || countAmmo(player) > 0;
    }

    public int countAmmo(Player player) {
        int total = 0;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack s = player.getInventory().getItem(i);
            if (s.is(ammoItem.get())) {
                total += s.getCount();
            }
        }
        return total;
    }

    private int consumeAmmo(Player player, int wanted) {
        int taken = 0;
        for (int i = 0; i < player.getInventory().getContainerSize() && taken < wanted; i++) {
            ItemStack s = player.getInventory().getItem(i);
            if (s.is(ammoItem.get())) {
                int n = Math.min(wanted - taken, s.getCount());
                s.shrink(n);
                taken += n;
            }
        }
        return taken;
    }

    protected static void playAt(Level level, Entity at, SoundEvent sound, float volume, float pitch) {
        level.playSound(null, at.getX(), at.getY(), at.getZ(), sound, SoundSource.PLAYERS, volume, pitch);
    }

    // ------------------------------------------------------------------ прочее
    @Override
    public boolean shouldCauseReequipAnimation(ItemStack oldStack, ItemStack newStack, boolean slotChanged) {
        return slotChanged;
    }

    @Override
    public boolean shouldCauseBlockBreakReset(ItemStack oldStack, ItemStack newStack) {
        return false;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.frontiermilitary.gun.ammo", getAmmo(stack), magSize).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable(automatic ? "tooltip.frontiermilitary.gun.hint_auto" : "tooltip.frontiermilitary.gun.hint_semi")
                .withStyle(ChatFormatting.DARK_GRAY));
    }

    @Override
    public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            @Override
            public HumanoidModel.ArmPose getArmPose(LivingEntity entity, InteractionHand hand, ItemStack stack) {
                return HumanoidModel.ArmPose.CROSSBOW_HOLD;
            }
        });
    }
}
