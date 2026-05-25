package com.pantrysaver.backend.controller;

import com.pantrysaver.backend.dto.CreateHouseholdRequest;
import com.pantrysaver.backend.dto.JoinHouseholdRequest;
import com.pantrysaver.backend.dto.UpdateHouseholdRequest;
import com.pantrysaver.backend.model.Household;
import com.pantrysaver.backend.model.User;
import com.pantrysaver.backend.service.HouseholdService;
import com.pantrysaver.backend.service.UserService;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/households")
public class HouseholdController {

    private final HouseholdService householdService;

    public HouseholdController(HouseholdService householdService) {
        this.householdService = householdService;
    }

    @GetMapping("/me")
    public Household getMyHousehold(@AuthenticationPrincipal Jwt jwt) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return householdService.getMyHousehold(userId);
    }

    @GetMapping("/me/members")
    public List<User> getMyHouseholdMembers(@AuthenticationPrincipal Jwt jwt) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return householdService.getMyHouseholdMembers(userId);
    }

    @PostMapping
    public Household createNewHousehold(@AuthenticationPrincipal Jwt jwt,
                                        @RequestBody CreateHouseholdRequest request) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return householdService.createNewHouseholdForUser(userId, request);
    }

    @PostMapping("/join")
    public Household joinHousehold(@AuthenticationPrincipal Jwt jwt,
                                   @RequestBody JoinHouseholdRequest request) {

        UUID userId = UUID.fromString(jwt.getSubject());
        UUID householdId = UUID.fromString(request.getHouseholdId());

        return householdService.joinHousehold(userId, householdId);
    }

    @PutMapping("/me")
    public Household updateMyHousehold(@AuthenticationPrincipal Jwt jwt,
                                       @RequestBody UpdateHouseholdRequest request) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return householdService.updateMyHousehold(userId, request);
    }

    @PostMapping("/leave")
    public Household leaveCurrentHousehold(@AuthenticationPrincipal Jwt jwt) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return householdService.leaveCurrentHousehold(userId);
    }

    @PostMapping("/households/generate-join-code")
    public ResponseEntity<Map<String, String>> generateJoinCode(@AuthenticationPrincipal Jwt jwt) {
    UUID userId = UUID.fromString(jwt.getSubject());
    String joinCode = householdService.generateJoinCode(userId);
    Map<String, String> response = new HashMap<>();
    response.put("join_code", joinCode);
    return ResponseEntity.ok(response);
    }
}