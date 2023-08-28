import axios from 'axios';
import { useEffect, useState } from 'react';

interface Transaction {
  id: number;
  name: string;
  amount: number;
  // fields based on the Django model
}

const Index = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const apiUrl = 'http://localhost:8000/transactions/';
    
    axios.get(apiUrl)
      .then(response => {
        setTransactions(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("There was an error fetching data", error);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          <h1>Transactions</h1>
          {transactions.map((transaction) => (
            <div key={transaction.id}>
              <p>{transaction.name}</p>
              <p>{transaction.amount}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Index;
