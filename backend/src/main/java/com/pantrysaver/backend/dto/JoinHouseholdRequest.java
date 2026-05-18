package com.pantrysaver.backend.dto;

// Data Transfer Object
// small class used to receive or send data through an API request/response

// receive the householdId from the frontend when a user wants to join a household
public class JoinHouseholdRequest {

    private String householdId;

    public String getHouseholdId() {
        return householdId;
    }

    public void setHouseholdId(String householdId) {
        this.householdId = householdId;
    }
}
