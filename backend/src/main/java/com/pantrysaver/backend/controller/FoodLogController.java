package com.pantrysaver.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.pantrysaver.backend.service.FoodlogService;
import com.pantrysaver.backend.request.*;

/**
 * accept HTTP requests and delegate to the service
 */
  @RestController
  @RequestMapping("/api/foodlog")  

public class FoodLogController {

  // inject the service class. May need @Autowired annotaions in older Spring versions

  private final FoodlogService foodlogService;  
  public FoodLogController(FoodlogService foodlogService) {this.foodlogService = foodlogService;}

  // define endpoints for recording purchase/discarding

  @PostMapping("/purchase")
  public ResponseEntity<String> logPurchase(@RequestBody PurchaseRequest request) {
    foodlogService.logPurchase(request);
    return ResponseEntity.ok("Success, purchase is logged!");
  }

  @PostMapping("/discard")
  public ResponseEntity<String> logDiscard(@RequestBody DiscardRequest request) {
      foodlogService.logDiscard(request);
      return ResponseEntity.ok("Success, discard is logged!");
  }

    
}
