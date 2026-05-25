package com.pantrysaver.backend.service;

import com.pantrysaver.backend.dto.CreateHouseholdRequest;
import com.pantrysaver.backend.dto.UpdateHouseholdRequest;
import com.pantrysaver.backend.model.Household;
import com.pantrysaver.backend.model.User;
import com.pantrysaver.backend.repository.HouseholdRepository;
import com.pantrysaver.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.security.SecureRandom;

@Service
public class HouseholdService {

    private final HouseholdRepository householdRepository;
    private final UserRepository userRepository;

    public HouseholdService(HouseholdRepository householdRepository,
                            UserRepository userRepository) {
        this.householdRepository = householdRepository;
        this.userRepository = userRepository;
    }

    public Household getMyHousehold(UUID userId) {

        User user = getUserOrThrow(userId);

        return user.getHousehold();
    }

    public List<User> getMyHouseholdMembers(UUID userId) {

        User user = getUserOrThrow(userId);

        UUID householdId = user.getHousehold().getId();

        return userRepository.findByHousehold_Id(householdId);
    }

    public Household createNewHouseholdForUser(UUID userId,
                                               CreateHouseholdRequest request) {

        User user = getUserOrThrow(userId);

        Household household = new Household();
        household.setId(UUID.randomUUID());
        household.setName(request.getName());
        household.setLocation(request.getLocation());

        Household savedHousehold = householdRepository.save(household);

        user.setHousehold(savedHousehold);
        userRepository.save(user);

        return savedHousehold;
    }

    public Household joinHousehold(UUID userId, UUID householdId) {

        User user = getUserOrThrow(userId);

        Household household = householdRepository.findById(householdId)
                .orElseThrow(() -> new RuntimeException("Household not found"));

        user.setHousehold(household);
        userRepository.save(user);

        return household;
    }

    public Household updateMyHousehold(UUID userId,
                                       UpdateHouseholdRequest request) {

        User user = getUserOrThrow(userId);

        Household household = user.getHousehold();

        if (request.getName() != null && !request.getName().isBlank()) {
            household.setName(request.getName());
        }

        if (request.getLocation() != null) {
            household.setLocation(request.getLocation());
        }

        return householdRepository.save(household);
    }

    public Household leaveCurrentHousehold(UUID userId) {

        User user = getUserOrThrow(userId);

        Household personalHousehold = new Household();
        personalHousehold.setId(UUID.randomUUID());
        personalHousehold.setName(user.getEmail() + "'s Household");
        personalHousehold.setLocation(null);

        Household savedHousehold = householdRepository.save(personalHousehold);

        user.setHousehold(savedHousehold);
        userRepository.save(user);

        return savedHousehold;
    }

    private User getUserOrThrow(UUID userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found. Call /auth/sync first."));
    }

    public String generateJoinCode(UUID userId) {
        User user = getUserOrThrow(userId);
        Household household = user.getHousehold();
        String joinCode = generateRandomCode(6);
        household.setJoinCode(joinCode);
        householdRepository.save(household);

        return joinCode;
    }

    private String generateRandomCode(int length) {
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        SecureRandom random = new SecureRandom();
        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            sb.append(chars.charAt(random.nextInt(chars.length())));
        }
        return sb.toString();
    }

    public Household joinByCode(UUID userId, String joinCode) {
        Household household = householdRepository.findByJoinCode(joinCode)
            .orElseThrow(() -> new RuntimeException("Invalid or expired join code"));
        User user = getUserOrThrow(userId);
        user.setHousehold(household);
        userRepository.save(user);
        household.setJoinCode(null);
        householdRepository.save(household);

        return household;
    }
}