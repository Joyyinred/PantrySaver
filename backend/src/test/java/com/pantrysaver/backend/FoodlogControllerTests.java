package com.pantrysaver.backend;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
public class FoodlogControllerTests {

    @LocalServerPort
    private int port;

    @Test
    void postPurchase_returnsOk() {
        Map<String, Object> body = new HashMap<>();
        body.put("householdId", UUID.randomUUID().toString());
        body.put("itemName", "Milk");
        body.put("quantity", 2.0);
        body.put("category", "Dairy");

        RestTemplate client = new RestTemplate();
        String url = "http://localhost:" + port + "/api/foodlog/purchase";

        ResponseEntity<String> response = client.postForEntity(url, body, String.class);

        assertEquals(200, response.getStatusCode().value());
    }

    @Test
    void postDiscard_returnsOk() {
        Map<String, Object> body = new HashMap<>();
        body.put("householdId", UUID.randomUUID().toString());
        body.put("itemName", "Bread");
        body.put("quantityDiscarded", 1.0);
        body.put("category", "Bakery");

        RestTemplate client = new RestTemplate();
        String url = "http://localhost:" + port + "/api/foodlog/discard";

        ResponseEntity<String> response = client.postForEntity(url, body, String.class);

        assertEquals(200, response.getStatusCode().value());
    }
}