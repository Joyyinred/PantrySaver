package com.pantrysaver.backend;

import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import com.pantrysaver.backend.repository.DiscardedItemRepository;
import com.pantrysaver.backend.repository.PurchasedItemRepository;
import com.pantrysaver.backend.request.DiscardRequest;
import com.pantrysaver.backend.request.PurchaseRequest;
import com.pantrysaver.backend.service.FoodlogService;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

/**
 * Test logging purchase, logging waste and 0 quantity entered.
 */

@SpringBootTest
@ActiveProfiles("test")
public class FoodlogServiceTests {

  @Autowired
  private FoodlogService foodlogService;

  @Autowired
  private PurchasedItemRepository purchasedItemRepository;

  @Autowired
  private DiscardedItemRepository discardedItemRepository;

  @Test
  void logPurchase_savesItem() {
      long before = purchasedItemRepository.count();

      PurchaseRequest request = new PurchaseRequest();
      request.setHouseholdId(UUID.randomUUID());
      request.setItemName("Milk-" + UUID.randomUUID());
      request.setQuantity(2.0);
      request.setCategory("Dairy");

      foodlogService.logPurchase(request);

      long after = purchasedItemRepository.count();
      assertEquals(before + 1, after);
  }

  @Test
  void logDiscard_savesItem() {
      long before = discardedItemRepository.count();

      DiscardRequest request = new DiscardRequest();
      request.setHouseholdId(UUID.randomUUID());
      request.setItemName("Bread-" + UUID.randomUUID());
      request.setQuantityDiscarded(1.0);
      request.setCategory("Bakery");

      foodlogService.logDiscard(request);

      long after = discardedItemRepository.count();
      assertEquals(before + 1, after);
  }

  @Test
  void logPurchase_throwsWhenQuantityIsZero() {
    PurchaseRequest request = new PurchaseRequest();
    request.setHouseholdId(UUID.randomUUID());
    request.setItemName("Milk");
    request.setQuantity(0.0);
    request.setCategory("Dairy");

    assertThrows(IllegalArgumentException.class, () -> foodlogService.logPurchase(request));
}



}