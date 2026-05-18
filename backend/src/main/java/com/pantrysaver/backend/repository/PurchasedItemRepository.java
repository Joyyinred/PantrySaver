package com.pantrysaver.backend.repository;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import com.pantrysaver.backend.model.PurchasedItem;

public interface PurchasedItemRepository extends JpaRepository<PurchasedItem, UUID> {}
