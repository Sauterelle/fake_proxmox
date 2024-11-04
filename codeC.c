#include <stdio.h>
#include <stdlib.h>
#include <libvirt/libvirt.h>
#include <unistd.h> // For sleep function

// Code de Louis Bignon, Guillaume Lorin et Quentin Prestifilippo, STI4A Apprentissage

void print_active_domains(virConnectPtr conn)
{
    printf("Active domain IDs:\n");
    int num_active_domains = virConnectNumOfDomains(conn);
    int *active_domains = malloc(num_active_domains * sizeof(int));
    num_active_domains = virConnectListDomains(conn, active_domains, num_active_domains);

    for (int i = 0; i < num_active_domains; i++)
    {
        virDomainPtr domain = virDomainLookupByID(conn, active_domains[i]);
        if (domain)
        {
            printf("ID: %d, Name: %s\n", active_domains[i], virDomainGetName(domain));

            virDomainInfo info;
            if (virDomainGetInfo(domain, &info) == 0)
            {
                printf("  State: %d\n", info.state);
                printf("  Max Memory: %lu KB\n", info.maxMem);
                printf("  Memory Used: %lu KB\n", info.memory);
                printf("  Number of Virtual CPUs: %d\n", info.nrVirtCpu);
                printf("  CPU Time: %llu ns\n", info.cpuTime);
            }
            virDomainFree(domain);
        }
    }
    free(active_domains);
}

void print_inactive_domains(virConnectPtr conn)
{
    printf("Inactive domain names:\n");
    int num_inactive_domains = virConnectNumOfDefinedDomains(conn);
    char **inactive_domains = malloc(num_inactive_domains * sizeof(char *));
    num_inactive_domains = virConnectListDefinedDomains(conn, inactive_domains, num_inactive_domains);

    for (int i = 0; i < num_inactive_domains; i++)
    {
        printf("  Name: %s\n", inactive_domains[i]);
        free(inactive_domains[i]); // Free each name string
    }
    free(inactive_domains); // Free the array
}

void shutdown_vm(virDomainPtr domain)
{
    printf("Forcing shutdown of domain: %s\n", virDomainGetName(domain));

    // Forcefully destroy the domain
    if (virDomainDestroy(domain) < 0)
    {
        fprintf(stderr, "Failed to force shutdown domain: %s\n", virDomainGetName(domain));
    }
    else
    {
        printf("Domain %s has been forcefully shut down.\n", virDomainGetName(domain));
    }
}

void start_vm(virDomainPtr domain)
{
    if (virDomainCreate(domain) < 0)
    {
        fprintf(stderr, "Failed to start domain: %s\n", virDomainGetName(domain));
    }
    else
    {
        printf("Starting domain: %s\n", virDomainGetName(domain));
    }
}

void suspend_vm(virDomainPtr domain)
{
    printf("Suspending domain: %s\n", virDomainGetName(domain));
    if (virDomainSuspend(domain) < 0)
    {
        fprintf(stderr, "Failed to suspend domain: %s\n", virDomainGetName(domain));
    }
    else
    {
        printf("Domain %s has been suspended.\n", virDomainGetName(domain));
    }
}

void save_vm(virDomainPtr domain)
{
    const char *save_path = "/var/lib/libvirt/qemu/save"; // Path to save state
    char *file_path = malloc(256 * sizeof(char));         // Buffer for file path
    snprintf(file_path, 256, "%s/%s.save", save_path, virDomainGetName(domain));

    if (virDomainSave(domain, file_path) < 0)
    {
        fprintf(stderr, "Failed to save domain: %s\n", virDomainGetName(domain));
    }
    else
    {
        printf("Domain %s has been saved to %s\n", virDomainGetName(domain), file_path);
    }

    free(file_path);
}

void resume_vm(virDomainPtr domain)
{
    printf("Resuming domain: %s\n", virDomainGetName(domain));
    if (virDomainCreate(domain) < 0)
    {
        fprintf(stderr, "Failed to resume domain: %s\n", virDomainGetName(domain));
    }
    else
    {
        printf("Domain %s has been resumed.\n", virDomainGetName(domain));
    }
}

void migrate_domains(virConnectPtr src_conn, virConnectPtr dest_conn)
{
    int num_active_domains = virConnectNumOfDomains(src_conn);
    int *active_domains = malloc(num_active_domains * sizeof(int));
    num_active_domains = virConnectListDomains(src_conn, active_domains, num_active_domains);

    for (int i = 0; i < num_active_domains; i++)
    {
        virDomainPtr domain = virDomainLookupByID(src_conn, active_domains[i]);
        if (domain)
        {
            const char *domain_name = virDomainGetName(domain);
            printf("Migrating domain: %s (ID: %d)\n", domain_name, active_domains[i]);

            // Attempt migration with unsafe settings
            unsigned int flags = VIR_MIGRATE_LIVE | VIR_MIGRATE_UNSAFE;
            // You can include other flags as necessary, e.g., VIR_DOMAIN_MIGRATE_UNSAFE

            // Attempt migration
            if (virDomainMigrate(domain, dest_conn, flags, NULL, NULL, NULL) < 0)
            {
                fprintf(stderr, "Failed to migrate domain %s\n", domain_name);
            }
            else
            {
                printf("Successfully migrated domain: %s\n", domain_name);
            }

            if (virDomainDestroy(domain) < 0)
            {
                fprintf(stderr, "Failed to destroy domain %s on source\n", domain_name);
            }
            else
            {
                printf("Successfully destroyed domain: %s on source\n", domain_name);
            }

            virDomainFree(domain);
        }
    }

    free(active_domains);
}

int main()
{
    const char *remote_user = "root";            // Replace with your remote username
    const char *remote_host = "192.168.146.128"; // Replace with your remote IP or hostname
    char connection_uri[256];

    snprintf(connection_uri, sizeof(connection_uri), "qemu+ssh://%s@%s/system", remote_user, remote_host);
    virConnectPtr conn = virConnectOpen(connection_uri);
    if (conn == NULL)
    {
        fprintf(stderr, "Failed to open connection to %s\n", connection_uri);
        return 1;
    }

    // Connection successful
    printf("Connection successful :)\n");

    const char *remote_user2 = "root";
    const char *remote_host2 = "192.168.146.128";
    char connection_uri2[256];

    snprintf(connection_uri2, sizeof(connection_uri2), "qemu+ssh://%s@%s/system", remote_user2, remote_host2);
    virConnectPtr conn2 = virConnectOpen(connection_uri2);
    if (conn2 == NULL)
    {
        fprintf(stderr, "Failed to open connection 2 to %s\n", connection_uri2);
        return 1;
    }

    // Connection successful
    printf("Connection 2 successful :)\n");

    // Display hostname
    const char *hostname = virConnectGetHostname(conn);
    if (hostname)
    {
        printf("Hostname: %s\n", hostname);
    }
    else
    {
        fprintf(stderr, "Failed to get hostname.\n");
    }

    // Check if connection is encrypted
    int encrypted = virConnectIsEncrypted(conn);
    printf("Connection is encrypted: %d\n", encrypted);

    // Maximum supported virtual CPUs
    int max_vcpus = virConnectGetMaxVcpus(conn, NULL);
    printf("Maximum supported virtual CPUs: %d\n", max_vcpus);

    // Total free memory on the host (in KB)
    unsigned long long memory = virNodeGetFreeMemory(conn);
    if (memory > 0)
    {
        printf("Memory size: %llu KB\n", memory);
    }
    else
    {
        fprintf(stderr, "Failed to get free memory.\n");
    }

    // Print active domains before shutting them down
    print_active_domains(conn);
    print_inactive_domains(conn);

    // Shutdown each active domain
    printf("\nShutting down active domains...\n");
    int num_active_domains = virConnectNumOfDomains(conn);
    int *active_domains = malloc(num_active_domains * sizeof(int));
    num_active_domains = virConnectListDomains(conn, active_domains, num_active_domains);

    for (int i = 0; i < num_active_domains; i++)
    {
        virDomainPtr domain = virDomainLookupByID(conn, active_domains[i]);
        if (domain)
        {
            shutdown_vm(domain);
            virDomainFree(domain);
        }
    }
    free(active_domains);

    // Display active and inactive domains after shutdown
    printf("\nAfter shutting down:\n");
    print_active_domains(conn);
    print_inactive_domains(conn);

    // Start each inactive domain
    printf("\nStarting inactive domains...\n");
    int num_inactive_domains = virConnectNumOfDefinedDomains(conn);
    char **inactive_domains = malloc(num_inactive_domains * sizeof(char *));
    num_inactive_domains = virConnectListDefinedDomains(conn, inactive_domains, num_inactive_domains);

    for (int i = 0; i < num_inactive_domains; i++)
    {
        virDomainPtr domain = virDomainLookupByName(conn, inactive_domains[i]);
        if (domain)
        {
            start_vm(domain);
            virDomainFree(domain);
        }
    }
    free(inactive_domains);

    // Display active and inactive domains after starting them
    printf("\nAfter starting:\n");
    print_active_domains(conn);
    print_inactive_domains(conn);

    // Suspend each active domain
    printf("\nSuspending active domains...\n");
    int num_active_domains = virConnectNumOfDomains(conn);
    int *active_domains = malloc(num_active_domains * sizeof(int));
    num_active_domains = virConnectListDomains(conn, active_domains, num_active_domains);

    for (int i = 0; i < num_active_domains; i++)
    {
        virDomainPtr domain = virDomainLookupByID(conn, active_domains[i]);
        if (domain)
        {
            suspend_vm(domain);
            save_vm(domain); // Save the state of the suspended VM
            virDomainFree(domain);
        }
    }
    free(active_domains);

    // Display active and inactive domains after suspending
    printf("\nAfter suspending:\n");
    print_active_domains(conn);
    print_inactive_domains(conn);

    // Resume each suspended domain
    printf("\nResuming suspended domains...\n");
    // Here we would typically load from the saved state,
    // but since we're only managing states here, we can reuse the inactive domain names.
    int num_inactive_domains = virConnectNumOfDefinedDomains(conn);
    char **inactive_domains = malloc(num_inactive_domains * sizeof(char *));
    num_inactive_domains = virConnectListDefinedDomains(conn, inactive_domains, num_inactive_domains);

    for (int i = 0; i < num_inactive_domains; i++)
    {
        virDomainPtr domain = virDomainLookupByName(conn, inactive_domains[i]);
        if (domain)
        {
            resume_vm(domain);
            virDomainFree(domain);
        }
    }

    // Freeing inactive_domains
    for (int i = 0; i < num_inactive_domains; i++)
    {
        free(inactive_domains[i]); // Free each name string
    }
    free(inactive_domains);

    // Display active and inactive domains after resuming
    printf("\nAfter resuming:\n");
    print_active_domains(conn);
    print_inactive_domains(conn);

    migrate_domains(conn, conn2);

    // Close the connection
    virConnectClose(conn);
    virConnectClose(conn2);
    printf("Connection closed.\n");

    return 0;
}
