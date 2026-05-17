package com.pantrysaver.backend.service;

import org.springframework.stereotype.Service;

import com.pantrysaver.backend.model.DiscardedItem;
import com.pantrysaver.backend.model.PurchasedItem;
import com.pantrysaver.backend.repository.DiscardedItemRepository;
import com.pantrysaver.backend.repository.PurchasedItemRepository;
import com.pantrysaver.backend.request.DiscardRequest;
import com.pantrysaver.backend.request.PurchaseRequest;

@Service
public class FoodlogService {
    // inject repos
    private final PurchasedItemRepository purchasedItemRepo;
    private final DiscardedItemRepository discardedItemRepo;

    public FoodlogService(PurchasedItemRepository purchasedItemRepo,
                          DiscardedItemRepository discardedItemRepo) {
        this.purchasedItemRepo = purchasedItemRepo;
        this.discardedItemRepo = discardedItemRepo;
    }

  /**
   * validates inforamtion sent from customer at front end
   * @param request the DTO encapsulating information sent from the client
   */
public void logPurchase(PurchaseRequest request) {
    if (request == null) {
        throw new IllegalArgumentException("Request cannot be null");
    }
    if (request.getHouseholdId() == null) {
        throw new IllegalArgumentException("HouseholdId is required");
    }
    if (request.getItemName() == null || request.getItemName().isBlank()) {
        throw new IllegalArgumentException("Item name is required");
    }
    if (request.getQuantity() <= 0) {
        throw new IllegalArgumentException("Quantity must be greater than 0");
    }

    PurchasedItem item = new PurchasedItem(
        request.getHouseholdId(),
        request.getItemName(),
        request.getQuantity(),
        request.getCategory()
    );

    purchasedItemRepo.save(item);
}

/**
 * validates discarded item info
 * @param request the DTO encapulating information sent from the client
 */
public void logDiscard(DiscardRequest request) {
    if (request == null) {
        throw new IllegalArgumentException("Request cannot be null");
    }
    if (request.getHouseholdId() == null) {
        throw new IllegalArgumentException("HouseholdId is required");
    }
    if (request.getItemName() == null || request.getItemName().isBlank()) {
        throw new IllegalArgumentException("Item name is required");
    }
    if (request.getQuantityDiscarded() <= 0) {
        throw new IllegalArgumentException("Quantity discarded must be greater than 0");
    }

    DiscardedItem item = new DiscardedItem(
        request.getHouseholdId(),
        request.getItemName(),
        request.getQuantityDiscarded(),
        request.getCategory()
    );

    discardedItemRepo.save(item);
}

}
