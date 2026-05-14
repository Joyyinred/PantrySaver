package com.pantrysaver.backend.model;

import java.time.LocalDateTime;
import java.util.*;
import jakarta.persistence.*;

@Entity
@Table(name = "purchased_items")
public class PurchasedItem {
  
  @Id
  // non-null
  private UUID id;

  @Column(name = "user_id")
  // non-null
  private UUID user_id;

  @Column(name = "household_id")
  // non-null
  private UUID household_id;

  @Column(name = "item_name")
  // non-null, is string
  private String item_name;

  @Column(name = "quantity")
  // non-null, is +ve double
  private double quantity;

  @Column(name = "category")
  // is string
  private String category;

  @Column(name = "logged_at")

  private LocalDateTime logged_at;

  public PurchasedItem() {}

  public PurchasedItem (

    UUID userId,
    UUID householdId,
    String itemName,
    Double quantity,
    String category
    ) {
    // no id?
    this.household_id = householdId;
    this.item_name = itemName;
    this.quantity = quantity;
    this.category = category;
    // may need to set logged time on the front end
    this.logged_at = LocalDateTime.now();  
    }
  

}
