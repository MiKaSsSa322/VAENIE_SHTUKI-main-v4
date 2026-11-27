package com.frontiermilitary.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Расчёт электросети: кабели, связанные друг с другом, питаются, если рядом с любым из них работает генератор. */
public final class PowerNet {
    private static final int MAX_CABLES = 512;

    private PowerNet() {}

    public static boolean isGeneratorOn(BlockState state) {
        return state.getBlock() instanceof GeneratorBlock && state.getValue(GeneratorBlock.STAGE) == 5;
    }

    /** Получает ли блок питание от соседнего генератора или питаемого кабеля. */
    public static boolean isFed(Level level, BlockPos pos) {
        for (Direction d : Direction.values()) {
            BlockState n = level.getBlockState(pos.relative(d));
            if (isGeneratorOn(n)) {
                return true;
            }
            if (n.getBlock() instanceof PowerCableBlock && n.getValue(PowerCableBlock.POWERED)) {
                return true;
            }
        }
        return false;
    }

    /** Пересчитывает сети вокруг позиции и обновляет подключённых потребителей (только сервер). */
    public static void refresh(Level level, BlockPos origin) {
        if (level.isClientSide) {
            return;
        }
        Set<BlockPos> done = new HashSet<>();
        List<BlockPos> starts = new ArrayList<>();
        starts.add(origin);
        for (Direction d : Direction.values()) {
            starts.add(origin.relative(d));
        }
        for (BlockPos start : starts) {
            BlockState state = level.getBlockState(start);
            if (state.getBlock() instanceof PowerCableBlock) {
                if (!done.contains(start)) {
                    refreshComponent(level, start, done);
                }
            } else if (state.getBlock() instanceof FloodlightBlock) {
                FloodlightBlock.update(level, start, state);
            }
        }
    }

    private static void refreshComponent(Level level, BlockPos start, Set<BlockPos> done) {
        List<BlockPos> component = new ArrayList<>();
        Deque<BlockPos> queue = new ArrayDeque<>();
        queue.add(start);
        done.add(start);
        boolean powered = false;
        while (!queue.isEmpty() && component.size() < MAX_CABLES) {
            BlockPos p = queue.poll();
            component.add(p);
            for (Direction d : Direction.values()) {
                BlockPos n = p.relative(d);
                BlockState ns = level.getBlockState(n);
                if (isGeneratorOn(ns)) {
                    powered = true;
                }
                if (ns.getBlock() instanceof PowerCableBlock && !done.contains(n)) {
                    done.add(n);
                    queue.add(n);
                }
            }
        }
        for (BlockPos p : component) {
            BlockState st = level.getBlockState(p);
            if (st.getValue(PowerCableBlock.POWERED) != powered) {
                level.setBlock(p, st.setValue(PowerCableBlock.POWERED, powered), 2);
            }
        }
        for (BlockPos p : component) {
            for (Direction d : Direction.values()) {
                BlockPos n = p.relative(d);
                BlockState ns = level.getBlockState(n);
                if (ns.getBlock() instanceof FloodlightBlock) {
                    FloodlightBlock.update(level, n, ns);
                }
            }
        }
    }
}
