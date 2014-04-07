package org.grails.samples

import com.newrelic.api.agent.Trace;
import com.newrelic.api.agent.NewRelic;

class PetclinicService {

	// PetController
	@Trace
	Pet createPet(String name, Date birthDate, long petTypeId, long ownerId) {
		def pet = new Pet(name: name, birthDate: birthDate, type: PetType.load(petTypeId), owner: Owner.load(ownerId))
		pet.save()
                NewRelic.recordMetric("AddingPet", 1);
		pet
	}
        @Trace
	void updatePet(Pet pet, String name, Date birthDate, long petTypeId, long ownerId) {
		pet.name = name
		pet.birthDate = birthDate
		pet.type = PetType.load(petTypeId)
		pet.owner = Owner.load(ownerId)
                NewRelic.recordMetric("ModifyingPet", 1);
                NewRelic.incrementCounter("ModifyingPet2");
		pet.save()
	}

        @Trace
	Visit createVisit(long petId, String description, Date date) {
		def visit = new Visit(pet: Pet.load(petId), description: description, date: date)
		visit.save()
		visit
	}

	// OwnerController
        @Trace
	Owner createOwner(String firstName, String lastName, String address, String city, String telephone) {
		def owner = new Owner(firstName: firstName, lastName: lastName, address: address, city: city, telephone: telephone)
		owner.save()
                NewRelic.noticeError(new Throwable("creatingOwner"));
		owner
	}
        @Trace
	void updateOwner(Owner owner, String firstName, String lastName, String address, String city, String telephone) {
		owner.firstName = firstName
		owner.lastName = lastName
		owner.address = address
		owner.city = city
		owner.telephone = telephone
                NewRelic.ignoreTransaction();
		owner.save()
	}
}
