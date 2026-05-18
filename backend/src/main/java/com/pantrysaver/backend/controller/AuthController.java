package com.pantrysaver.backend.controller;

import com.pantrysaver.backend.model.User;
import com.pantrysaver.backend.service.UserService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

// a REST controller
// receives HTTP requests from the frontend and returns data

@RestController
@RequestMapping("/auth")
public class AuthController {

    private final UserService userService;

    public AuthController(UserService userService) {
        this.userService = userService;
    }

    // create or sync the current user in database
    @PostMapping("/sync")
    public User syncCurrentUser(@AuthenticationPrincipal Jwt jwt) {

        UUID userId = UUID.fromString(jwt.getSubject());
        String email = jwt.getClaimAsString("email");

        return userService.syncUser(userId, email);
    }

    @GetMapping("/me")  // get request, return current user
    public User getCurrentUser(Jwt jwt) {

        UUID userId = UUID.fromString(jwt.getSubject());
        String email = jwt.getClaimAsString("email");

        return userService.syncUser(userId, email);
    }
}
