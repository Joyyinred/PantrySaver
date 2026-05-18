package com.pantrysaver.backend.service;

import com.pantrysaver.backend.model.Household;
import com.pantrysaver.backend.model.User;
import com.pantrysaver.backend.repository.HouseholdRepository;
import com.pantrysaver.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final HouseholdRepository householdRepository;

    public UserService(UserRepository userRepository,
                       HouseholdRepository householdRepository) {
        this.userRepository = userRepository;
        this.householdRepository = householdRepository;
    }
    
    // since supabase already handles register/login
    // what we do here is to make sure the user exists
    // connecting Supabase Auth identity to app’s own data model.
    public User syncUser(UUID userId, String email) {

        return userRepository.findById(userId)
                .map(existingUser -> {
                    if (!existingUser.getEmail().equals(email)) {
                        existingUser.setEmail(email);
                        return userRepository.save(existingUser);
                    }
                    return existingUser;
                })
                .orElseGet(() -> {
                    Household household = new Household();
                    household.setId(UUID.randomUUID());
                    household.setName(email + "'s Household");
                    household.setLocation(null);

                    Household savedHousehold = householdRepository.save(household);

                    User user = new User();
                    user.setId(userId);
                    user.setEmail(email);
                    user.setHousehold(savedHousehold);

                    return userRepository.save(user);
                });
    }

    public User getCurrentUserProfile(UUID userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }
    
    // Join household
    public User joinHousehold(UUID userId, UUID householdId) {

        User user = getCurrentUserProfile(userId);

        Household household = householdRepository.findById(householdId)
                .orElseThrow(() -> new RuntimeException("Household not found"));

        user.setHousehold(household);

        return userRepository.save(user);
    }
    
    //  Update user details
    public User updateUserEmail(UUID userId, String newEmail) {

        User user = getCurrentUserProfile(userId);

        user.setEmail(newEmail);

        return userRepository.save(user);
    }
}