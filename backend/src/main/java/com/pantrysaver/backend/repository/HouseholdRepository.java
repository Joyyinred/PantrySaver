package com.pantrysaver.backend.repository;


import com.pantrysaver.backend.model.Household;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface HouseholdRepository extends JpaRepository<Household, UUID> {
}
