package com.pantrysaver.backend.controller;

import com.pantrysaver.backend.dto.JoinHouseholdRequest;
import com.pantrysaver.backend.model.User;
import com.pantrysaver.backend.service.UserService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/me")
    public User getMyProfile(@AuthenticationPrincipal Jwt jwt) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return userService.getCurrentUserProfile(userId);
    }

    @PostMapping("/me/household")
    public User joinHousehold(@AuthenticationPrincipal Jwt jwt,
                              @RequestBody JoinHouseholdRequest request) {

        UUID userId = UUID.fromString(jwt.getSubject());
        UUID householdId = UUID.fromString(request.getHouseholdId());

        return userService.joinHousehold(userId, householdId);
    }
}