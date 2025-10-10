from collections import defaultdict

# Example resource_blocks with a Date field
resource_blocks = [
    {
        "Id": "872629d8-b43a-4db9-9abe-b30200a13b4c",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "60fef859-f32a-4f29-be3b-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-20T09:47:01Z",
        "UpdatedUtc": "2025-06-20T09:47:01Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "200135c5-2e5e-4875-b57a-b30100a455cb",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "a307609f-ef96-4910-b21b-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-19T09:58:19Z",
        "UpdatedUtc": "2025-06-19T09:58:19Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "c6a7ca17-9f1c-45a5-ba64-b30100a453b4",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "0d60d6da-1a54-4fe0-9390-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-19T09:58:17Z",
        "UpdatedUtc": "2025-06-19T09:58:17Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "39dd82a8-d92c-4058-ab6d-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "fd9da0c9-05f8-4b0d-8839-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "c1a94d70-4b29-438c-a297-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "99f19408-02db-47e8-9cdc-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "6844c467-af5d-4d6c-a0b6-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "7739a5c8-4c7b-4289-8823-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "f4f6aeef-4b31-46bc-a081-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "34012f94-ea12-41a1-ab3c-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "69eceeab-2fba-41af-993d-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "60c5cdb6-04d0-430b-b0a0-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "8a1ab98b-b398-4840-91a4-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "795da2c9-d098-4487-8157-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "d5f939e2-2bdf-431a-8b90-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "aab61f67-e463-49dd-b912-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "c576c460-c3fd-472b-885e-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "06b8c555-99c7-469d-9b90-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "bb7277e1-c407-4d90-8552-b2fe00d74f80",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "915856cb-0791-41d1-9992-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-24T14:00:00Z",
        "EndUtc": "2025-06-25T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:55Z",
        "UpdatedUtc": "2025-06-16T13:03:55Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "c2cf42da-4840-4c06-b8bc-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "60c5cdb6-04d0-430b-b0a0-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "5cb6f7ca-7314-4194-b777-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "aab61f67-e463-49dd-b912-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "4e2a1f71-b554-43d6-b39e-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "eac2f2a3-1ac3-4654-affe-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "5f50fe55-9617-447e-a7b9-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "7739a5c8-4c7b-4289-8823-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "7644272f-57c0-42b3-a355-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "915856cb-0791-41d1-9992-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "ea84dc12-e9f8-41da-a1db-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "34012f94-ea12-41a1-ab3c-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "fd9a363e-4709-476c-9e1a-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "795da2c9-d098-4487-8157-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "bdbd6acf-d12d-46d8-952a-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "99f19408-02db-47e8-9cdc-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "6e81fa60-1b5e-45fd-91ad-b2fe00d74f16",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "06b8c555-99c7-469d-9b90-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-23T14:00:00Z",
        "EndUtc": "2025-06-24T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "127074b1-5ddf-499a-ba9f-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "aab61f67-e463-49dd-b912-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "89490cb2-b6ec-47b7-ba05-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "915856cb-0791-41d1-9992-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "c2d3f5e4-680d-48dd-b3a0-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "795da2c9-d098-4487-8157-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "03d0db0f-e66d-447c-af2a-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "7739a5c8-4c7b-4289-8823-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "e035cd5f-4391-44c5-9cea-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "34012f94-ea12-41a1-ab3c-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "6a89842b-edcd-4c1b-9c2b-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "99f19408-02db-47e8-9cdc-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "17ee0d6b-bba9-40e8-97a1-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "eac2f2a3-1ac3-4654-affe-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "1930e788-4a31-4de5-8858-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "fd9da0c9-05f8-4b0d-8839-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "348be049-42ee-468b-8843-b2fe00d74e88",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "60c5cdb6-04d0-430b-b0a0-b2fc0115b917",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T08:00:00Z",
        "CreatedUtc": "2025-06-16T13:03:54Z",
        "UpdatedUtc": "2025-06-16T13:03:54Z",
        "DeletedUtc": None,
        "Name": "Blocked",
        "Notes": None
    },
    {
        "Id": "8017692a-a685-4104-bcca-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "96799fa4-c965-4c25-a3eb-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "4096ba5b-8ccc-48af-bc23-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "bddf5f09-70f6-4ccf-99a0-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "34e63069-74b1-4cee-b820-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "91e6a077-a12f-47be-9fe0-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "0945c607-2ae2-4812-b53d-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "fbd98ccd-f0b9-4546-8282-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "ff4a518d-b8c0-46e7-b493-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "81c6a639-9301-483e-98b4-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "feb85be6-afc4-4979-b293-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "05d930f5-c46d-481c-a91f-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "a422af26-b2ca-429b-b232-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "7e0ba03e-d1de-4c8a-959f-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "1087212c-4f60-4a45-aecd-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "ae794ffd-28f8-4e81-a3dd-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "befca8b6-78b6-4df9-ae1c-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "549c0089-d615-4ee8-a09e-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "43184fd5-b255-4312-adc0-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "033dfc99-2b2a-48aa-9321-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "5dfddd34-734e-4816-ac90-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "8adeb4b4-9971-425e-9e1c-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "889ab07d-5f39-41c0-aa28-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "11f017f0-5bd6-450e-8a0b-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "6310b184-0fe5-4fef-a78c-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "9cf5d4eb-9341-4945-9e96-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "c7308ad6-326f-4aff-a495-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "a84c92d7-4e2d-4ed5-85b7-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "e040015f-446a-45ac-a024-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "9605d6b8-36cf-4d15-a438-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "f9b9364f-bd1f-4d9b-9ee0-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "c33300b0-fdde-4904-8a8b-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "30564258-8477-44c8-9d77-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "49ba3d95-dcc7-431c-a8ec-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "8de3cca6-477e-46b9-9be6-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "bcfec0fc-d41c-4ddb-8c06-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "b7b4abe8-1e6c-44d7-9919-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "9e1ac72e-40c5-4fde-9d9c-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "7c306c2c-c519-45e7-973c-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "1392c28b-5d72-40b9-835d-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "4edc47e0-0fc7-4207-9716-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "8c9b41a3-908d-49fa-8aac-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "493cf1fc-5497-43b9-94c4-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "0008a92f-068b-4295-8078-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "46b5de23-570f-4ba9-909a-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "c6536260-de76-4db8-a964-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "f464da84-595b-449d-8fbf-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "42d8fd56-e69c-4b4c-919b-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "82d58abb-3b69-4488-8fbb-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "0866adc9-35dc-455b-9a77-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "cd987be7-0f6a-45e5-8ee3-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "e1a4b1e3-5975-4dd2-a2ac-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "349c0470-c527-4208-8df9-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "430aa271-14d4-40ce-9197-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "5936c6c6-87c3-4f80-8b00-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "85cc402c-c797-407a-a067-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "a9276c57-8fac-42ee-899a-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "c56b3e6f-95d0-4aa0-8ef2-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "6aa0687b-c2c1-44cf-82b6-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "0df8cfbe-ad2e-4e47-9e3e-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "4fb23df8-817b-409a-8003-b2fb013e4373",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "d870e311-b521-408b-a51c-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "47a049ec-1732-487a-b12e-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "05bd4c16-0763-4ebc-aa30-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "194b39a9-b46b-48b8-b0f7-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "a2433008-5244-4d56-b11b-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "509a3850-86e2-49ae-ad16-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "56309f75-773d-4c87-aa45-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "ad98b7db-684b-4738-a82c-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "fb42a1bb-205a-40e0-b07b-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "94caebee-8a59-4515-a610-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "cb1298e7-0fe0-48d7-aef2-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "5c9771fc-de82-41f4-a5b9-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "a6cd3b38-9a68-4cd7-bfdc-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "70782a94-cb40-44c9-a446-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "8292a4a4-9547-4ef5-b7d9-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "a76f2d60-2a1f-4b54-a0d5-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "891acaae-bfbd-4fe3-aff6-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "b3c9780c-252a-4ce6-a09e-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "bf27c713-9d44-4918-bd98-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "ccc908b2-a132-4af0-9c0c-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "fcf82020-c779-4ca1-b1bf-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "13c77e5f-bc82-42e9-993b-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "91b17cab-0c47-4a1a-b3b7-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "16f796c5-2745-442f-92f0-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "601a607d-a88f-4af0-a9b5-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "38c32667-297c-4122-92b2-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "fafced63-1fe6-46d8-b8bf-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "e99300cc-0ba9-475c-928b-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "44eb6c98-8194-4f23-be58-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "be36b38e-bdd7-48d7-90ac-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "606ca647-2179-4175-b7f1-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "59a51665-9267-4c84-8a6d-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "cd164061-3e17-4771-b6b3-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "cc30b557-9283-4a48-87bb-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "cce96534-c05f-4a52-bca3-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    },
    {
        "Id": "26180bb4-6283-4607-812f-b2fb013e4372",
        "EnterpriseId": "5e43687f-6b76-42ed-8d7d-b12b0089dc3d",
        "AssignedResourceId": "cf7ad454-2467-428c-bd68-b12b008f5235",
        "IsActive": True,
        "Type": "OutOfOrder",
        "StartUtc": "2025-06-22T14:00:00Z",
        "EndUtc": "2025-06-23T13:59:00Z",
        "CreatedUtc": "2025-06-13T19:18:45Z",
        "UpdatedUtc": "2025-06-13T19:18:45Z",
        "DeletedUtc": None,
        "Name": "Automated order",
        "Notes": None
    }
]

space_mapping = {
    2: {
      "Hotel": '853f72c9-00a7-44dd-8287-b329008c3ba5',
      "Student": '35560efe-7735-49be-90a6-b329008c3ba5',
      "Extended Stay": 'f0690c62-afaa-4646-b8ec-b329008c3ba5'
    },
    3: {
      "Hotel": 'dba8b98c-1af6-41b8-a533-b329008c3ba5',
      "Student": '39df5e41-ac49-44fd-a57a-b329008c3ba5',
      "Extended Stay": '21dd95d1-0348-45e0-a0c4-b329008c3ba5'
    },
    4: {
      "Hotel": '63c52ac2-2e92-4e4e-a545-b329008c3ba5',
      "Student": '706e4efd-5a5e-43a9-9a12-b329008c3ba5',
      "Extended Stay": 'ed3b9972-1cbf-41ca-8db6-b329008c3ba5'
    },
    5: {
      "Hotel": 'f4d4bef9-3903-4af3-84a1-b329008c3ba5',
      "Student": '9fb1ffec-5a6f-465c-8c69-b329008c3ba5',
      "Extended Stay": '66fdbb26-8251-404b-85a1-b329008c3ba5'
    },
    6: {
      "Hotel": '2af005a5-a41e-4bb6-9254-b329008c3ba5',
      "Student": '1062398e-fd5f-47c1-9c3e-b329008c3ba5',
      "Extended Stay": '1214e4a3-b875-4d59-845c-b329008c3ba5'
    }
}

# Step 1: Group blocked resource IDs by date
blocked_by_date = defaultdict(set)
for block in resource_blocks:
    blocked_by_date[block["StartUtc"].split('T')[0]].add(block["AssignedResourceId"])

# Step 2: For each date, print which resource types are not blocked for each space
for date, blocked_ids in blocked_by_date.items():
    print(f"\nDate: {date}")
    for space_num, types in space_mapping.items():
        not_blocked = []
        for rtype, rid in types.items():
            if rid not in blocked_ids:
                not_blocked.append(rtype)
        if not_blocked:
            print(f"  Space {space_num} not blocked: {', '.join(not_blocked)}")
        else:
            print(f"  Space {space_num} is fully blocked.")


'''
        blocks.forEach(block => {
          const assignedId = block.AssignedResourceId;
          const start = new Date(block.StartUtc);
          const end = new Date(block.EndUtc);

          for (let d = new Date(start); d < end; d.setDate(d.getDate() + 1)) {
            const formattedDate = Utilities.formatDate(new Date(d), timezone, 'yyyy-MM-dd');

            // Match date to column in headerRow
            const colIndex = headerRow.findIndex(h => {
              // h might be a date or string, ensure correct format
              if (h instanceof Date) {
                return Utilities.formatDate(h, timezone, 'yyyy-MM-dd') === formattedDate;
              } else if (typeof h === 'string') {
                return h === formattedDate;
              }
              return false;
            });

            if (colIndex === -1) {
              Logger.log(`Date ${formattedDate} not found in header row`);
              continue;
            }

            // Find matching row for AssignedResourceId
            let row = null;
            for (let r = 2; r <= 6; r++) {
              for (const type in resourceIdMap[r]) {
                if (resourceIdMap[r][type] === assignedId) {
                  row = rowOffset + r;
                  break;
                }
              }
              if (row !== null) break;
            }

            if (row !== null) {
              const col = 2 + colIndex; // Columns start at B = 2
              sheet.getRange(row, col).setValue("Occupied");
            } else {
              Logger.log(`Block not found for AssignedResourceId: ${assignedId}`);
            }
          }
        });
'''