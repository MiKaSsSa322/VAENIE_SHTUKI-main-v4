package com.frontiermilitary.block;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Обычный блок с нестандартной формой (бочка, «ёж», маскировочная сеть). */
public class ShapedBlock extends Block {
    private final VoxelShape shape;

    public ShapedBlock(Properties properties, double x1, double y1, double z1, double x2, double y2, double z2) {
        super(properties);
        this.shape = Block.box(x1, y1, z1, x2, y2, z2);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return shape;
    }
}
