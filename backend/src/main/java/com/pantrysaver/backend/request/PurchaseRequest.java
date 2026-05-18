package com.pantrysaver.backend.request;

import java.util.UUID;
// import java.util.List;

/**
 * A DTO for purchased item
 */

public class PurchaseRequest {
    private UUID householdId;
    private String itemName;
    private double quantity;
    private String category;

    public PurchaseRequest() {}

    public UUID getHouseholdId() {
        return householdId;
    }

    public void setHouseholdId(UUID householdId) {
        this.householdId = householdId;
    }

    public String getItemName() {
        return itemName;
    }

    public void setItemName(String itemName) {
        this.itemName = itemName;
    }

    public double getQuantity() {
        return quantity;
    }

    public void setQuantity(double quantity) {
        this.quantity = quantity;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }
}
