package com.frontiermilitary.block;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Колючая проволока: без коллизии, сильно замедляет и ранит движущихся существ (как сладкие ягоды). */
public class RazorWireBlock extends Block {
    private static final VoxelShape SHAPE = Block.box(0.0D, 0.0D, 0.0D, 16.0D, 9.0D, 16.0D);

    public RazorWireBlock(Properties properties) {
        super(properties);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!(entity instanceof LivingEntity)) {
            return;
        }
        entity.makeStuckInBlock(state, new Vec3(0.6D, 0.5D, 0.6D));
        if (!level.isClientSide) {
            double dx = Math.abs(entity.getX() - entity.xOld);
            double dz = Math.abs(entity.getZ() - entity.zOld);
            if (dx >= 0.003D || dz >= 0.003D) {
                entity.hurt(level.damageSources().cactus(), 1.0F);
            }
        }
    }
}
