package com.frontiermilitary.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Силовой кабель: соединяется со всеми соседними кабелями, генераторами и прожекторами; несёт питание. */
public class PowerCableBlock extends Block {
    public static final BooleanProperty NORTH = BooleanProperty.create("north");
    public static final BooleanProperty EAST = BooleanProperty.create("east");
    public static final BooleanProperty SOUTH = BooleanProperty.create("south");
    public static final BooleanProperty WEST = BooleanProperty.create("west");
    public static final BooleanProperty UP = BooleanProperty.create("up");
    public static final BooleanProperty DOWN = BooleanProperty.create("down");
    public static final BooleanProperty POWERED = BooleanProperty.create("powered");

    private static final VoxelShape CORE = Block.box(6.5D, 6.5D, 6.5D, 9.5D, 9.5D, 9.5D);
    private static final VoxelShape ARM_N = Block.box(6.5D, 6.5D, 0.0D, 9.5D, 9.5D, 6.5D);
    private static final VoxelShape ARM_S = Block.box(6.5D, 6.5D, 9.5D, 9.5D, 9.5D, 16.0D);
    private static final VoxelShape ARM_W = Block.box(0.0D, 6.5D, 6.5D, 6.5D, 9.5D, 9.5D);
    private static final VoxelShape ARM_E = Block.box(9.5D, 6.5D, 6.5D, 16.0D, 9.5D, 9.5D);
    private static final VoxelShape ARM_D = Block.box(6.5D, 0.0D, 6.5D, 9.5D, 6.5D, 9.5D);
    private static final VoxelShape ARM_U = Block.box(6.5D, 9.5D, 6.5D, 9.5D, 16.0D, 9.5D);

    public PowerCableBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(NORTH, false).setValue(EAST, false).setValue(SOUTH, false)
                .setValue(WEST, false).setValue(UP, false).setValue(DOWN, false).setValue(POWERED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(NORTH, EAST, SOUTH, WEST, UP, DOWN, POWERED);
    }

    public static boolean canConnect(BlockState state) {
        return state.getBlock() instanceof PowerCableBlock
                || state.getBlock() instanceof GeneratorBlock
                || state.getBlock() instanceof FloodlightBlock;
    }

    private static BooleanProperty property(Direction d) {
        switch (d) {
            case NORTH: return NORTH;
            case EAST: return EAST;
            case SOUTH: return SOUTH;
            case WEST: return WEST;
            case UP: return UP;
            default: return DOWN;
        }
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos();
        BlockState state = this.defaultBlockState();
        for (Direction d : Direction.values()) {
            state = state.setValue(property(d), canConnect(level.getBlockState(pos.relative(d))));
        }
        return state;
    }

    @Override
    @SuppressWarnings("deprecation")
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighborState,
                                  LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        return state.setValue(property(direction), canConnect(neighborState));
    }

    @Override
    @SuppressWarnings("deprecation")
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        VoxelShape shape = CORE;
        if (state.getValue(NORTH)) shape = Shapes.or(shape, ARM_N);
        if (state.getValue(SOUTH)) shape = Shapes.or(shape, ARM_S);
        if (state.getValue(WEST)) shape = Shapes.or(shape, ARM_W);
        if (state.getValue(EAST)) shape = Shapes.or(shape, ARM_E);
        if (state.getValue(DOWN)) shape = Shapes.or(shape, ARM_D);
        if (state.getValue(UP)) shape = Shapes.or(shape, ARM_U);
        return shape;
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean moving) {
        if (!oldState.is(state.getBlock())) {
            PowerNet.refresh(level, pos);
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moving) {
        super.onRemove(state, level, pos, newState, moving);
        if (!state.is(newState.getBlock())) {
            PowerNet.refresh(level, pos);
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void neighborChanged(BlockState state, Level level, BlockPos pos, Block block, BlockPos fromPos, boolean moving) {
        PowerNet.refresh(level, pos);
    }
}
