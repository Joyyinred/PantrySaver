package com.pantrysaver.backend.repository;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import com.pantrysaver.backend.model.DiscardedItem;

public interface DiscardedItemRepository extends JpaRepository<DiscardedItem, UUID> {}