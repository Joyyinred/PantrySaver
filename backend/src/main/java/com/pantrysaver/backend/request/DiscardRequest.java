package com.pantrysaver.backend.request;

// import java.util.List;
import java.util.UUID;

/**
 * A DTO for discarded items
 */

public class DiscardRequest {
    private UUID householdId;
    private String itemName;
    private double quantityDiscarded;
    private String category;

    public DiscardRequest() {}

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

    public double getQuantityDiscarded() {
        return quantityDiscarded;
    }

    public void setQuantityDiscarded(double quantityDiscarded) {
        this.quantityDiscarded = quantityDiscarded;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }
}